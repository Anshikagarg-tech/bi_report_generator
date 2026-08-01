"""
Turns a raw DataFrame into a compact, structured JSON profile:
shape, dtypes, missingness, distributions, correlations, top categories,
time trends (if a date-like column is found), and outliers.

This structured profile - NOT the raw rows - is what gets sent to the LLM.
That keeps prompts small, keeps sensitive raw records out of the model call
if desired, and keeps numbers ground-truthed in pandas rather than the model.
"""
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.config import settings


def _is_datetime_like(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if series.dtype == object or pd.api.types.is_string_dtype(series):
        sample = series.dropna().astype(str).head(20)
        if sample.empty:
            return False
        parsed = pd.to_datetime(sample, errors="coerce")
        return parsed.notna().mean() > 0.8
    return False


def _numeric_stats(series: pd.Series) -> Dict[str, Any]:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return {}
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    outliers = s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)]
    return {
        "min": float(s.min()),
        "max": float(s.max()),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "std": float(s.std()) if len(s) > 1 else 0.0,
        "q1": float(q1),
        "q3": float(q3),
        "outlier_count": int(len(outliers)),
        "outlier_pct": round(len(outliers) / len(s) * 100, 2),
    }


def _categorical_stats(series: pd.Series, top_n: int = 8) -> Dict[str, Any]:
    vc = series.astype(str).value_counts(dropna=True).head(top_n)
    total = series.notna().sum()
    return {
        "top_values": [
            {"value": str(k), "count": int(v), "pct": round(v / total * 100, 2) if total else 0}
            for k, v in vc.items()
        ],
        "cardinality": int(series.nunique(dropna=True)),
    }


def _trend_for_date_col(df: pd.DataFrame, date_col: str, numeric_cols: List[str]) -> Dict[str, Any]:
    tmp = df[[date_col] + numeric_cols].copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna(subset=[date_col])
    if tmp.empty:
        return {}

    span_days = (tmp[date_col].max() - tmp[date_col].min()).days
    freq = "ME" if span_days > 60 else "D"
    grouped = tmp.set_index(date_col).resample(freq)[numeric_cols].sum(numeric_only=True)

    trends = {}
    for col in numeric_cols:
        series = grouped[col].dropna()
        if len(series) < 2:
            continue
        first, last = series.iloc[0], series.iloc[-1]
        pct_change = ((last - first) / first * 100) if first != 0 else None
        peak_idx = series.idxmax()
        trough_idx = series.idxmin()
        trends[col] = {
            "period_start": str(series.index[0].date()),
            "period_end": str(series.index[-1].date()),
            "start_value": float(first),
            "end_value": float(last),
            "pct_change": round(pct_change, 2) if pct_change is not None else None,
            "peak_period": str(peak_idx.date()),
            "peak_value": float(series.max()),
            "trough_period": str(trough_idx.date()),
            "trough_value": float(series.min()),
        }
    return {
        "date_column": date_col,
        "granularity": "monthly" if freq == "ME" else "daily",
        "series": trends,
    }


def profile_dataframe(df: pd.DataFrame, focus_columns: Optional[List[str]] = None) -> Dict[str, Any]:
    if len(df) > settings.MAX_PROFILE_ROWS:
        df = df.sample(settings.MAX_PROFILE_ROWS, random_state=42)

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    date_cols = [c for c in df.columns if _is_datetime_like(df[c])]
    categorical_cols = [c for c in df.columns if c not in numeric_cols and c not in date_cols]

    columns_profile = []
    for col in df.columns:
        series = df[col]
        missing = int(series.isna().sum())
        entry = {
            "name": col,
            "dtype": str(series.dtype),
            "role": "numeric" if col in numeric_cols else ("date" if col in date_cols else "categorical"),
            "missing_count": missing,
            "missing_pct": round(missing / len(df) * 100, 2) if len(df) else 0,
            "unique_count": int(series.nunique(dropna=True)),
        }
        if col in numeric_cols:
            entry["stats"] = _numeric_stats(series)
        elif col in categorical_cols:
            entry["stats"] = _categorical_stats(series)
        columns_profile.append(entry)

    correlations = {}
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True).round(3)
        pairs = []
        for i, a in enumerate(numeric_cols):
            for b in numeric_cols[i + 1:]:
                val = corr.loc[a, b]
                if pd.notna(val) and abs(val) >= 0.5:
                    pairs.append({"a": a, "b": b, "correlation": float(val)})
        pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        correlations = {"strong_pairs": pairs[:10]}

    trend = {}
    if date_cols and numeric_cols:
        trend = _trend_for_date_col(df, date_cols[0], numeric_cols[:5])

    duplicate_rows = int(df.duplicated().sum())

    profile = {
        "shape": {"rows": int(len(df)), "columns": int(df.shape[1])},
        "column_roles": {
            "numeric": numeric_cols,
            "categorical": categorical_cols,
            "date": date_cols,
        },
        "columns": columns_profile,
        "correlations": correlations,
        "trend": trend,
        "data_quality": {
            "duplicate_rows": duplicate_rows,
            "duplicate_pct": round(duplicate_rows / len(df) * 100, 2) if len(df) else 0,
            "columns_with_missing": [
                c["name"] for c in columns_profile if c["missing_count"] > 0
            ],
        },
        "focus_columns": focus_columns or [],
    }
    return profile
