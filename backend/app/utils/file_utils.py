import json
import uuid
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from app.config import settings


def new_dataset_id() -> str:
    return uuid.uuid4().hex[:12]


def dataset_dir(dataset_id: str) -> Path:
    d = settings.REPORTS_DIR / dataset_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "charts").mkdir(exist_ok=True)
    return d


def read_tabular(path: Path) -> pd.DataFrame:
    """Read CSV/TSV/XLSX into a DataFrame, sniffing delimiter for text files."""
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t")
    # default: CSV, let pandas sniff the separator
    try:
        return pd.read_csv(path, sep=None, engine="python")
    except Exception:
        return pd.read_csv(path)


def save_upload(dataset_id: str, filename: str, content: bytes) -> Path:
    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    dest = settings.UPLOADS_DIR / f"{dataset_id}_{filename}"
    dest.write_bytes(content)
    return dest


def save_json(dataset_id: str, name: str, data: Dict[str, Any]) -> Path:
    d = dataset_dir(dataset_id)
    path = d / name
    path.write_text(json.dumps(data, indent=2, default=str))
    return path


def load_json(dataset_id: str, name: str) -> Dict[str, Any]:
    path = dataset_dir(dataset_id) / name
    return json.loads(path.read_text())
