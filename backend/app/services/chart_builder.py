"""
Generates a handful of high-signal charts from the profiled data:
- time trend line chart (if a date column exists)
- top-N bar chart for the leading categorical column
- correlation heatmap (if 2+ strong numeric correlations)
- distribution histogram for the highest-variance numeric column
Saved as PNGs under storage/reports/<dataset_id>/charts/
"""
from pathlib import Path
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from app.utils.file_utils import dataset_dir

plt.rcParams.update({"figure.autolayout": True, "font.size": 10})


def _save(fig, dataset_id: str, filename: str) -> str:
    charts_dir = dataset_dir(dataset_id) / "charts"
    path = charts_dir / filename
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return filename


def build_charts(df: pd.DataFrame, profile: Dict[str, Any], dataset_id: str) -> List[Dict[str, str]]:
    charts: List[Dict[str, str]] = []
    numeric_cols = profile["column_roles"]["numeric"]
    categorical_cols = profile["column_roles"]["categorical"]
    date_cols = profile["column_roles"]["date"]

    # 1. Trend line chart
    trend = profile.get("trend") or {}
    if trend.get("series"):
        date_col = trend["date_column"]
        tmp = df[[date_col] + list(trend["series"].keys())].copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
        tmp = tmp.dropna(subset=[date_col]).set_index(date_col)
        freq = "ME" if trend["granularity"] == "monthly" else "D"
        grouped = tmp.resample(freq).sum(numeric_only=True)
        top_metric = list(trend["series"].keys())[0]

        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.plot(grouped.index, grouped[top_metric], marker="o", linewidth=2, color="#2563eb")
        ax.set_title(f"{top_metric} over time")
        ax.set_xlabel("")
        ax.set_ylabel(top_metric)
        ax.grid(alpha=0.3)
        fname = _save(fig, dataset_id, "trend_" + top_metric.replace(" ", "_") + ".png")
        charts.append({"title": f"{top_metric} Trend", "type": "line", "filename": fname})

    # 2. Top category bar chart
    if categorical_cols:
        # pick categorical column with reasonable cardinality
        candidates = [c for c in profile["columns"] if c["name"] in categorical_cols and 1 < c["unique_count"] <= 30]
        if candidates:
            col = sorted(candidates, key=lambda c: c["unique_count"])[0]
            top_values = col["stats"]["top_values"][:8]
            labels = [v["value"] for v in top_values]
            counts = [v["count"] for v in top_values]

            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.barh(labels[::-1], counts[::-1], color="#0ea5e9")
            ax.set_title(f"Top values in '{col['name']}'")
            ax.set_xlabel("Count")
            fname = _save(fig, dataset_id, f"top_{col['name']}.png")
            charts.append({"title": f"Top {col['name']} Categories", "type": "bar", "filename": fname})

    # 3. Correlation heatmap
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True)
        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_xticklabels(numeric_cols, rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(numeric_cols, fontsize=8)
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=7)
        fig.colorbar(im, ax=ax, shrink=0.8)
        ax.set_title("Correlation Heatmap")
        fname = _save(fig, dataset_id, "correlation_heatmap.png")
        charts.append({"title": "Correlation Heatmap", "type": "heatmap", "filename": fname})

    # 4. Distribution histogram for highest-variance numeric column
    if numeric_cols:
        num_entries = [c for c in profile["columns"] if c["name"] in numeric_cols and c.get("stats")]
        if num_entries:
            top = max(num_entries, key=lambda c: c["stats"].get("std", 0))
            series = pd.to_numeric(df[top["name"]], errors="coerce").dropna()
            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.hist(series, bins=30, color="#22c55e", edgecolor="white")
            ax.set_title(f"Distribution of {top['name']}")
            ax.set_xlabel(top["name"])
            ax.set_ylabel("Frequency")
            fname = _save(fig, dataset_id, f"dist_{top['name']}.png")
            charts.append({"title": f"Distribution of {top['name']}", "type": "histogram", "filename": fname})

    return charts
