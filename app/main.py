"""FastAPI entrypoint for FRAS backend."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.report_service import (
    ReportValidationError,
    generate_report,
    get_report_by_id,
    get_report_history,
)
from app.report_templates import report_templates

app = FastAPI(title="File Report Automation System")
public_dir = Path("public")


@app.get("/api/report-templates")
def list_report_templates() -> dict[str, list[dict[str, object]]]:
    return {"templates": report_templates}


@app.get("/api/reports/history")
def report_history() -> dict[str, list[dict[str, object]]]:
    return {"history": get_report_history()}


@app.post("/api/reports/generate", status_code=201)
def create_report(payload: dict) -> dict[str, dict]:
    try:
        report = generate_report(payload)
        return {"report": report}
    except ReportValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/reports/{report_id}/download/{format_name}")
def download_report(report_id: str, format_name: str) -> FileResponse:
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    export_entry = next((entry for entry in report["exports"] if entry["format"] == format_name), None)
    if not export_entry:
        raise HTTPException(status_code=404, detail="Export format not found for this report")

    file_path = Path(export_entry["path"]).resolve()
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found")

    return FileResponse(file_path, media_type="application/pdf", filename=f"{report_id}.{format_name}")


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


if public_dir.exists():
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")
