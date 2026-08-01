# Automated BI Report Generator

Upload a CSV/TSV/XLSX file → get a GenAI-drafted business intelligence report:
executive summary, KPIs, narrative sections, charts, data-quality notes, and
recommendations — grounded in numbers computed by pandas, narrated by Claude.

## How it works

```
CSV/XLSX upload
      │
      ▼
pandas profiling  ──►  structured JSON profile (stats, correlations, trends,
(data_profiler.py)      missingness, outliers) — the "ground truth"
      │
      ├──► chart_builder.py ──► matplotlib PNGs (trend, top categories,
      │                          correlation heatmap, distribution)
      │
      └──► report_generator.py ──► Claude API (JSON-mode prompt) ──►
                                     natural-language BI report
```

The LLM never sees or invents raw numbers on its own — it narrates a
pre-computed statistical profile, which keeps the report factually grounded
and lets you audit exactly what data went into the prompt (`storage/reports/<id>/profile.json`).

## Folder structure

```
bi-report-generator/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + CORS
│   │   ├── config.py                # env-based settings
│   │   ├── api/routes.py            # /upload, /analyze, /charts, /report
│   │   ├── models/schemas.py        # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── data_profiler.py     # pandas stats/correlation/trend engine
│   │   │   ├── chart_builder.py     # matplotlib chart generation
│   │   │   └── report_generator.py  # Claude prompt + JSON parsing + markdown
│   │   └── utils/file_utils.py      # upload/storage helpers
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # upload → preview → generate → report flow
│   │   ├── api/client.js            # fetch wrappers for backend API
│   │   └── components/
│   │       ├── FileUpload.jsx
│   │       ├── LoadingState.jsx
│   │       ├── KpiCards.jsx
│   │       ├── ChartsGrid.jsx
│   │       └── ReportView.jsx
│   ├── index.html / vite.config.js / package.json
│   └── Dockerfile
├── sample_data/sample_sales.csv       # try it immediately with this
├── docker-compose.yml
└── README.md
```

## Setup (local, no Docker)

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then add your ANTHROPIC_API_KEY
python run.py                # http://localhost:8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                  # http://localhost:5173
```

Open `http://localhost:5173`, upload `sample_data/sample_sales.csv`, and click
**Generate BI Report**.

## Setup (Docker)

```bash
cp backend/.env.example backend/.env   # add your ANTHROPIC_API_KEY
docker compose up --build
```

## API reference

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/upload` | Upload a file, get `dataset_id` + preview |
| POST | `/api/analyze` | Run profiling + chart generation + LLM narrative for a `dataset_id` |
| GET  | `/api/charts/{dataset_id}/{filename}` | Serve a generated chart PNG |
| GET  | `/api/report/{dataset_id}/download` | Download the report as Markdown |

`POST /api/analyze` body:
```json
{
  "dataset_id": "abc123",
  "business_context": "Optional: what this data represents / what to focus on",
  "focus_columns": ["revenue", "region"]
}
```

## Extending this

- **Bigger files**: `MAX_PROFILE_ROWS` in `.env` samples large datasets before
  profiling; swap the in-memory `_REGISTRY` in `routes.py` for a database/S3
  for multi-user, persistent deployments.
- **Export to Word/PowerPoint/PDF**: the report is already structured JSON
  (`report.json`) — feed it into a docx/pptx/pdf generator for polished
  downloadable deliverables.
- **Scheduled reports**: wrap `/api/analyze` in a cron job / Celery task
  pointed at a recurring data export (e.g. a nightly DB dump to CSV).
- **Multiple LLM providers**: `report_generator.py` isolates all Claude calls
  behind `generate_narrative_report()` — swap the client there only.
