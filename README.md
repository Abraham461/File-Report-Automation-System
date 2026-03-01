# File & Report Automation System

Report module with:
- template definitions (title, sections, placeholders, required fields)
- report generation endpoint that binds selected files and metadata
- generated report storage and generation history
- PDF exports with downloadable links
- frontend flow: template selection, source selection, preview, export/save

## Run

```bash
npm start
```

Open http://localhost:3000.

## API

- `GET /api/report-templates`
- `POST /api/reports/generate`
- `GET /api/reports/history`
- `GET /api/reports/:reportId/download/:format`
