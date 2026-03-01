# Architecture Overview

## Monorepo

- `backend`: Express API with separated domain modules.
- `frontend`: Vite SPA shell for dashboard and reporting workflows.
- `docs`: technical documentation.
- `infra`: local and deployment manifests.

## Backend Domains

- `auth`: authentication and authorization entrypoints.
- `files`: upload/list/index operations.
- `reports`: report generation and templates.
- `search`: global query endpoints.
- `users`: user profile and administration flows.

## Request Flow

1. Frontend loads app shell and calls backend `/health`.
2. UI screens invoke `/api/*` domain endpoints.
3. Backend modules coordinate storage/database services from env config.
