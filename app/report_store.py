"""Storage layer for generated reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STORAGE_PATH = Path("storage/generatedReports.json")


def ensure_store() -> None:
    if not STORAGE_PATH.exists():
        STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STORAGE_PATH.write_text(json.dumps({"reports": [], "history": []}, indent=2), encoding="utf-8")


def read_store() -> dict[str, Any]:
    ensure_store()
    return json.loads(STORAGE_PATH.read_text(encoding="utf-8"))


def write_store(data: dict[str, Any]) -> None:
    ensure_store()
    STORAGE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def append_report(report_record: dict[str, Any]) -> dict[str, Any]:
    store = read_store()
    store["reports"].append(report_record)
    store["history"].insert(
        0,
        {
            "reportId": report_record["id"],
            "generatedAt": report_record["generatedAt"],
            "templateId": report_record["templateId"],
            "title": report_record["title"],
            "exports": [entry["format"] for entry in report_record["exports"]],
        },
    )
    write_store(store)
    return report_record
