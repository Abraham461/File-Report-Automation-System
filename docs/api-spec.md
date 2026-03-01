# FRAS Canonical API Contract

This document defines the canonical API contract for the File Report Automation System (FRAS).

## Base URL

- Local: `http://localhost:3000`
- Test/deployed: `${FRAS_BASE_URL}`

## Content type

- Request bodies: `application/json`
- Response bodies: `application/json` unless noted otherwise.

## Endpoints

### Health

- `GET /health`
- Response `200`: `{ "ok": true }`

### Upload

- `POST /api/upload`
- Request body:

```json
{
  "files": [
    { "name": "contract-001.pdf" }
  ]
}
```

- Validation:
  - Body must be a JSON object.
  - `files` must be a non-empty array.
- Response `201`:

```json
{
  "upload": {
    "accepted": 1,
    "receivedAt": "2026-03-01T08:00:00.000Z"
  }
}
```

- Response `400`: `{ "error": "..." }`

### Search

- `GET /api/search?q=<term>`
- Validation:
  - `q` is required and cannot be blank.
- Response `200`:

```json
{
  "query": "report",
  "results": [
    {
      "type": "template",
      "id": "file-summary-report",
      "title": "File Summary Report",
      "description": "...",
      "url": "http://localhost:3000/api/report-templates#file-summary-report"
    }
  ]
}
```

- Response `400`: `{ "error": "q query parameter is required" }`

### Templates

- `GET /api/report-templates`
- Response `200`: `{ "templates": [...] }`

### Report generation (canonical path)

- `POST /api/reports`
- Request body:

```json
{
  "templateId": "file-summary-report",
  "metadata": { "reportDate": "2026-03-01", "preparedBy": "Automation Bot" },
  "files": [{ "name": "contract-001.pdf", "sizeBytes": 120000, "status": "approved" }],
  "activityEvents": [],
  "exportFormats": ["pdf"]
}
```

- Response `201`: `{ "report": {...} }`
- Response `400`: `{ "error": "..." }`

### Report generation (compatibility alias)

- `POST /api/reports/generate`
- Behavior is identical to `POST /api/reports`.
- Clients should migrate to `POST /api/reports`.

### Report history

- `GET /api/reports/history`
- Response `200`: `{ "history": [...] }`

### Report by ID

- `GET /api/reports/{reportId}`
- Response `200`: `{ "report": {...} }`
- Response `404`: `{ "error": "Report not found" }`

### Report export download

- `GET /api/reports/{reportId}/download/pdf`
- Response `200`: PDF file stream
- Response `404`: `{ "error": "Report not found" }` or `{ "error": "Export format not found for this report" }`

## UI route availability

The following pages must return HTTP `200` and render keyword-matching content:

- `/login` (contains `login`)
- `/upload` (contains `upload`)
- `/search` (contains `search`)
- `/reports` (contains `reports` or `report`)

