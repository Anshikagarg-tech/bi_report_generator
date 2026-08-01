"""
Generates a business intelligence report using a local Ollama model.

The statistical profile is calculated by the backend first.
The AI model only converts those verified numbers into a readable
business intelligence report.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import settings


SYSTEM_PROMPT = """You are a senior business intelligence analyst.

You will be given a JSON statistical profile of a tabular dataset.
The statistics have already been calculated by the backend.

Your job is to write a clear, decision-useful BI report for business
stakeholders.

IMPORTANT RULES:
- Only use numbers that appear in the provided profile.
- Never invent or alter numbers.
- Do not calculate new statistics.
- Be specific and reference actual column names and values.
- Write in plain business English.
- Mention important missing values or duplicate records if present.
- Keep the executive summary to 3-5 sentences.
- Recommendations must be concrete and connected to the findings.
- Return ONLY valid JSON.
- Do not use markdown.
- Do not add explanations outside the JSON.

Return exactly this structure:

{
  "title": "descriptive report title",
  "executive_summary": "3-5 sentence summary",
  "kpis": [
    {
      "label": "metric name",
      "value": "value",
      "delta": "string or null"
    }
  ],
  "sections": [
    {
      "heading": "section heading",
      "content": "2-5 sentence analysis"
    }
  ],
  "data_quality_notes": [
    "note"
  ],
  "recommendations": [
    "actionable recommendation"
  ]
}
"""


def _build_user_prompt(
    profile: Dict[str, Any],
    business_context: Optional[str]
) -> str:

    context_line = ""

    if business_context:
        context_line = (
            f"\nBusiness context provided by the user:\n"
            f"{business_context}\n"
        )

    return f"""
Here is the verified statistical profile of the dataset:

{json.dumps(profile, indent=2, default=str)}

{context_line}

Create the BI report using ONLY the information above.
Return only valid JSON.
"""


def _call_ollama(prompt: str) -> str:
    """Send the prompt to the local Ollama server."""

    payload = {
        "model": settings.OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.2
        }
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        settings.OLLAMA_URL,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))

        return result.get("response", "")

    except urllib.error.URLError as e:
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running on your computer."
        ) from e

    except Exception as e:
        raise RuntimeError(
            f"Ollama request failed: {str(e)}"
        ) from e


def _parse_json_response(text: str) -> Dict[str, Any]:
    """Convert Ollama's response into the format expected by the API."""

    cleaned = text.strip()

    # Remove markdown code fences if the model adds them.
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].strip().lower() in ("```json", "```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned)

    except json.JSONDecodeError:
        return {
            "title": "Business Intelligence Report",
            "executive_summary": cleaned[:1000],
            "kpis": [],
            "sections": [
                {
                    "heading": "Analysis",
                    "content": cleaned
                }
            ],
            "data_quality_notes": [],
            "recommendations": []
        }

    # ---------------------------------------------------------
    # Normalize KPIs
    # ---------------------------------------------------------

    normalized_kpis = []

    for kpi in data.get("kpis", []):
        if not isinstance(kpi, dict):
            continue

        normalized_kpis.append({
            "label": str(kpi.get("label", "")),
            "value": str(kpi.get("value", "")),
            "delta": (
                None
                if kpi.get("delta") is None
                else str(kpi.get("delta"))
            )
        })

    data["kpis"] = normalized_kpis

    # ---------------------------------------------------------
    # Normalize sections
    # ---------------------------------------------------------

    normalized_sections = []

    for section in data.get("sections", []):
        if not isinstance(section, dict):
            continue

        normalized_sections.append({
            "heading": str(section.get("heading", "")),
            "content": str(section.get("content", ""))
        })

    data["sections"] = normalized_sections

    # ---------------------------------------------------------
    # Normalize data quality notes
    # ---------------------------------------------------------

    normalized_notes = []

    for note in data.get("data_quality_notes", []):
        if isinstance(note, dict):
            # Convert an object into readable text.
            normalized_notes.append(
                " ".join(
                    str(value)
                    for value in note.values()
                )
            )
        else:
            normalized_notes.append(str(note))

    data["data_quality_notes"] = normalized_notes

    # ---------------------------------------------------------
    # Normalize recommendations
    # ---------------------------------------------------------

    normalized_recommendations = []

    for recommendation in data.get("recommendations", []):

        if isinstance(recommendation, dict):

            # Ollama may return:
            # {"actionable_recommendation": "..."}
            if "actionable_recommendation" in recommendation:
                normalized_recommendations.append(
                    str(
                        recommendation[
                            "actionable_recommendation"
                        ]
                    )
                )

            else:
                # Convert any other dictionary into text.
                normalized_recommendations.append(
                    " ".join(
                        str(value)
                        for value in recommendation.values()
                    )
                )

        else:
            normalized_recommendations.append(
                str(recommendation)
            )

    data["recommendations"] = normalized_recommendations

    # ---------------------------------------------------------
    # Normalize title and summary
    # ---------------------------------------------------------

    data["title"] = str(
        data.get(
            "title",
            "Business Intelligence Report"
        )
    )

    data["executive_summary"] = str(
        data.get(
            "executive_summary",
            ""
        )
    )

    return data


def generate_narrative_report(
    profile: Dict[str, Any],
    business_context: Optional[str] = None,
) -> Dict[str, Any]:

    prompt = _build_user_prompt(
        profile,
        business_context
    )

    # Generate report using local Ollama model.
    text = _call_ollama(prompt)

    # Convert AI response into structured JSON.
    data = _parse_json_response(text)

    data["generated_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    return data


def render_markdown(
    report: Dict[str, Any],
    charts: List[Dict[str, str]]
) -> str:

    lines = [
        f"# {report['title']}",
        "",
        f"_Generated {report['generated_at']}_",
        ""
    ]

    lines += [
        "## Executive Summary",
        "",
        report["executive_summary"],
        ""
    ]

    if report.get("kpis"):
        lines.append("## Key Metrics")
        lines.append("")
        lines.append("| Metric | Value | Change |")
        lines.append("|---|---|---|")

        for kpi in report["kpis"]:
            lines.append(
                f"| {kpi['label']} | "
                f"{kpi['value']} | "
                f"{kpi.get('delta') or '-'} |"
            )

        lines.append("")

    for section in report.get("sections", []):
        lines += [
            f"## {section['heading']}",
            "",
            section["content"],
            ""
        ]

    if charts:
        lines.append("## Visuals")
        lines.append("")

        for chart in charts:
            lines.append(
                f"![{chart['title']}]"
                f"(charts/{chart['filename']})"
            )
            lines.append("")

    if report.get("data_quality_notes"):
        lines.append("## Data Quality Notes")
        lines.append("")

        for note in report["data_quality_notes"]:
            lines.append(f"- {note}")

        lines.append("")

    if report.get("recommendations"):
        lines.append("## Recommendations")
        lines.append("")

        for recommendation in report["recommendations"]:
            lines.append(f"- {recommendation}")

        lines.append("")

    return "\n".join(lines)
