from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    column_names: List[str]
    preview: List[Dict[str, Any]]


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    missing_count: int
    missing_pct: float
    unique_count: int
    stats: Dict[str, Any] = {}


class ChartInfo(BaseModel):
    title: str
    type: str
    filename: str
    url: str
    insight: Optional[str] = None


class KpiCard(BaseModel):
    label: str
    value: str
    delta: Optional[str] = None


class ReportResponse(BaseModel):
    dataset_id: str
    title: str
    generated_at: str
    kpis: List[KpiCard]
    executive_summary: str
    sections: List[Dict[str, str]]   # {"heading": ..., "content": ...}
    recommendations: List[str]
    charts: List[ChartInfo]
    data_quality_notes: List[str]
    markdown_report: str


class AnalyzeRequest(BaseModel):
    dataset_id: str
    business_context: Optional[str] = None
    focus_columns: Optional[List[str]] = None
