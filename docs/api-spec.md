# API Starter Specification

## Health

- `GET /health`
  - Response: `{ status: "ok", service: "fra-backend", timestamp: "..." }`

## Domain Stubs

- `GET /api/auth`
- `GET /api/files`
- `GET /api/reports`
- `GET /api/search`
- `GET /api/users`

Each domain endpoint currently returns a readiness message and should be expanded with full CRUD and workflow routes.
