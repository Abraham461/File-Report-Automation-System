"""Seed script for local/dev environments."""

from uuid import uuid4

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Report

SEED_TEMPLATE_ID = 'incident-summary'


def main() -> None:
    with SessionLocal() as session:
        existing = session.execute(
            select(Report).where(Report.template_id == SEED_TEMPLATE_ID)
        ).scalars().first()
        if existing:
            print('Seed data already present; skipping.')
            return

        report = Report(
            id=str(uuid4()),
            template_id=SEED_TEMPLATE_ID,
            report_metadata={
                'incident_id': 'INC-0001',
                'owner': 'seed-user',
                'severity': 'low',
            },
        )
        session.add(report)
        session.commit()
        print(f'Seeded report {report.id}')


if __name__ == '__main__':
    main()
