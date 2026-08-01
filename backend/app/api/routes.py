from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.models.schemas import AnalyzeRequest, ReportResponse, UploadResponse
from app.services import chart_builder, data_profiler, report_generator
from app.utils.file_utils import (
    dataset_dir,
    load_json,
    new_dataset_id,
    read_tabular,
    save_json,
    save_upload,
)

router = APIRouter()

# very small in-memory registry mapping dataset_id -> uploaded file path.
# Swap for a real DB in production.
_REGISTRY: dict[str, str] = {}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    allowed = (".csv", ".tsv", ".xlsx", ".xls")
    if not file.filename.lower().endswith(allowed):
        raise HTTPException(400, f"Unsupported file type. Allowed: {allowed}")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(400, "Uploaded file is empty.")

    dataset_id = new_dataset_id()
    path = save_upload(dataset_id, file.filename, content)
    _REGISTRY[dataset_id] = str(path)

    try:
        df = read_tabular(path)
    except Exception as e:
        raise HTTPException(400, f"Could not parse file: {e}")

    if df.empty:
        raise HTTPException(400, "Parsed dataset has zero rows.")

    preview = df.head(10).fillna("").astype(str).to_dict(orient="records")

    return UploadResponse(
        dataset_id=dataset_id,
        filename=file.filename,
        rows=len(df),
        columns=df.shape[1],
        column_names=list(df.columns.astype(str)),
        preview=preview,
    )


@router.post("/analyze", response_model=ReportResponse)
async def analyze(request: AnalyzeRequest):
    path = _REGISTRY.get(request.dataset_id)
    if not path:
        raise HTTPException(404, "Unknown dataset_id. Upload the file again.")

    df = read_tabular(__import__("pathlib").Path(path))

    profile = data_profiler.profile_dataframe(df, focus_columns=request.focus_columns)
    save_json(request.dataset_id, "profile.json", profile)

    charts = chart_builder.build_charts(df, profile, request.dataset_id)

    try:
        report = report_generator.generate_narrative_report(
            profile, business_context=request.business_context
        )
    except RuntimeError as e:
        # e.g. missing ANTHROPIC_API_KEY - a clear, actionable message instead of a 500
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(502, f"Report generation failed: {e}")

    save_json(request.dataset_id, "report.json", report)

    chart_infos = [
        {
            "title": c["title"],
            "type": c["type"],
            "filename": c["filename"],
            "url": f"/api/charts/{request.dataset_id}/{c['filename']}",
        }
        for c in charts
    ]

    markdown_report = report_generator.render_markdown(report, charts)
    md_path = dataset_dir(request.dataset_id) / "report.md"
    md_path.write_text(markdown_report)

    return ReportResponse(
        dataset_id=request.dataset_id,
        title=report["title"],
        generated_at=report["generated_at"],
        kpis=report.get("kpis", []),
        executive_summary=report["executive_summary"],
        sections=report.get("sections", []),
        recommendations=report.get("recommendations", []),
        charts=chart_infos,
        data_quality_notes=report.get("data_quality_notes", []),
        markdown_report=markdown_report,
    )


@router.get("/charts/{dataset_id}/{filename}")
async def get_chart(dataset_id: str, filename: str):
    path = dataset_dir(dataset_id) / "charts" / filename
    if not path.exists():
        raise HTTPException(404, "Chart not found.")
    return FileResponse(path)


@router.get("/report/{dataset_id}/download")
async def download_report(dataset_id: str):
    path = dataset_dir(dataset_id) / "report.md"
    if not path.exists():
        raise HTTPException(404, "Report not found. Run /analyze first.")
    return FileResponse(path, filename=f"bi_report_{dataset_id}.md", media_type="text/markdown")
