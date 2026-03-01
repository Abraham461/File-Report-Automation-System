"""Core report generation service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.export_service import export_to_pdf
from app.report_store import append_report, read_store
from app.report_templates import get_template_by_id


class ReportValidationError(ValueError):
    """Raised when report payload validation fails."""


def validate_required_fields(template: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []

    for field in template["requiredFields"]:
        if field == "fileList" and (not payload.get("files")):
            missing.append(field)
        elif field == "activityEvents" and (not payload.get("activityEvents")):
            missing.append(field)
        elif field not in {"fileList", "activityEvents"} and not payload.get("metadata", {}).get(field):
            missing.append(field)

    return missing


def render_status_breakdown(files: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for file in files:
        status = file.get("status") or "unknown"
        counts[status] = counts.get(status, 0) + 1
    return "\n".join(f"- {status}: {count}" for status, count in counts.items())


def render_file_table(files: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"{index + 1}. {file.get('name')} | owner: {file.get('owner', 'n/a')} | "
        f"category: {file.get('category', 'n/a')} | size: {file.get('size', 'n/a')} | "
        f"status: {file.get('status', 'n/a')}"
        for index, file in enumerate(files)
    )


def render_risk_findings(events: list[dict[str, Any]]) -> str:
    risky = [event for event in events if event.get("type") in {"delete", "permission-change", "failed-login"}]
    if not risky:
        return "No high-risk findings identified."
    return "\n".join(
        f"- [{event.get('timestamp')}] {event.get('actor')} performed {event.get('type')} on {event.get('target')}"
        for event in risky
    )


def render_event_timeline(events: list[dict[str, Any]]) -> str:
    sorted_events = sorted(events, key=lambda event: event.get("timestamp", ""))
    return "\n".join(
        f"{event.get('timestamp')} | {event.get('actor')} | {event.get('type')} | {event.get('target')}"
        for event in sorted_events
    )


def template_context(template_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    files = payload.get("files", [])
    events = payload.get("activityEvents", [])

    if template_id == "file-summary-report":
        return {
            **payload.get("metadata", {}),
            "fileCount": len(files),
            "totalSize": f"{sum(int(file.get('sizeBytes') or 0) for file in files)} bytes",
            "statusBreakdown": render_status_breakdown(files),
            "fileTable": render_file_table(files),
        }

    if template_id == "activity-audit-report":
        return {
            **payload.get("metadata", {}),
            "eventCount": len(events),
            "uniqueActors": len({event.get('actor') for event in events}),
            "riskFindings": render_risk_findings(events),
            "eventTimeline": render_event_timeline(events),
        }

    return payload.get("metadata", {})


def apply_template(template: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    rendered_sections: list[dict[str, Any]] = []

    for section in template["sections"]:
        body = section["body"]
        for placeholder in template["placeholders"]:
            value = context.get(placeholder, f"{{{{{placeholder}}}}}")
            body = body.replace(f"{{{{{placeholder}}}}}", str(value))
        rendered_sections.append({**section, "body": body})

    full_text = "\n\n".join(
        [template["title"], *[f"{section['heading']}\n{section['body']}" for section in rendered_sections]]
    )
    return {"renderedSections": rendered_sections, "fullText": full_text}


def generate_report(payload: dict[str, Any]) -> dict[str, Any]:
    template = get_template_by_id(payload.get("templateId", ""))
    if not template:
        raise ReportValidationError("Template not found")

    missing_fields = validate_required_fields(template, payload)
    if missing_fields:
        raise ReportValidationError(f"Missing required fields: {', '.join(missing_fields)}")

    context = template_context(template["id"], payload)
    rendered = apply_template(template, context)
    report_id = str(uuid4())

    exports: list[dict[str, str]] = []
    requested_formats = payload.get("exportFormats") or ["pdf"]
    for format_name in requested_formats:
        if format_name == "pdf":
            pdf_path = export_to_pdf(report_id, rendered["fullText"])
            exports.append(
                {
                    "format": format_name,
                    "path": str(pdf_path),
                    "downloadUrl": f"/api/reports/{report_id}/download/pdf",
                }
            )

    if not exports:
        pdf_path = export_to_pdf(report_id, rendered["fullText"])
        exports.append({"format": "pdf", "path": str(pdf_path), "downloadUrl": f"/api/reports/{report_id}/download/pdf"})

    report_record = {
        "id": report_id,
        "templateId": template["id"],
        "title": payload.get("title") or template["title"],
        "metadata": payload.get("metadata", {}),
        "files": payload.get("files", []),
        "activityEvents": payload.get("activityEvents", []),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sections": rendered["renderedSections"],
        "fullText": rendered["fullText"],
        "exports": [
            {
                **entry,
                "path": str(Path(entry["path"]).resolve().relative_to(Path.cwd())),
            }
            for entry in exports
        ],
    }

    return append_report(report_record)


def get_report_history() -> list[dict[str, Any]]:
    return read_store()["history"]


def get_report_by_id(report_id: str) -> dict[str, Any] | None:
    return next((report for report in read_store()["reports"] if report["id"] == report_id), None)
