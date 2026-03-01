from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Report

app = FastAPI(title='File & Report Automation System API', version='1.0.0')

REPORT_TEMPLATES = [
    {
        'id': 'incident-summary',
        'title': 'Incident Summary',
        'required_fields': ['incident_id', 'owner', 'severity'],
    },
    {
        'id': 'audit-package',
        'title': 'Audit Evidence Package',
        'required_fields': ['audit_period', 'auditor'],
    },
]


class GenerateReportRequest(BaseModel):
    template_id: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReportResponse(BaseModel):
    id: str
    template_id: str
    metadata: dict[str, Any]
    created_at: datetime


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/health')
def health() -> dict[str, bool]:
    return {'ok': True}


@app.get('/api/report-templates')
def get_report_templates() -> dict[str, list[dict[str, Any]]]:
    return {'templates': REPORT_TEMPLATES}


@app.post('/api/reports/generate', status_code=201)
def generate_report(payload: GenerateReportRequest, db: Session = Depends(get_db)) -> dict[str, ReportResponse]:
    report = Report(id=str(uuid4()), template_id=payload.template_id, report_metadata=payload.metadata)
    db.add(report)
    db.commit()
    db.refresh(report)
    return {
        'report': ReportResponse(
            id=report.id,
            template_id=report.template_id,
            metadata=report.report_metadata,
            created_at=report.created_at,
        )
    }


@app.get('/api/reports/history')
def get_report_history(db: Session = Depends(get_db)) -> dict[str, list[ReportResponse]]:
    records = db.execute(select(Report).order_by(Report.created_at.desc())).scalars().all()
    return {
        'history': [
            ReportResponse(
                id=report.id,
                template_id=report.template_id,
                metadata=report.report_metadata,
                created_at=report.created_at,
            )
            for report in records
        ]
    }
