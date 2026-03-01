# File & Report Automation System

Report module with:
- template definitions (title, sections, placeholders, required fields)
- report generation endpoint that binds selected files and metadata
- generated report storage and generation history
- PDF exports with downloadable links
- frontend flow: template selection, source selection, preview, export/save

## Run (Python backend default)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

Or via script:

```bash
npm start
```

Open http://localhost:3000.

## API

- `GET /api/report-templates`
- `POST /api/reports/generate`
- `GET /api/reports/history`
- `GET /api/reports/:reportId/download/:format`

## Migration status

Runtime parity has been reached for template listing, report generation, history retrieval, and report download in `app/`. Node runtime modules in `src/` are now deprecated and retained only for reference during transition.
