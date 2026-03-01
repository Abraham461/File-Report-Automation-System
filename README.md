# File & Report Automation System

A monorepo starter layout for a file and report automation platform with a Node.js backend and Vite frontend.

## Repository Layout

```text
.
├── backend/        # API service and domain modules
├── frontend/       # UI app shell and feature pages
├── docs/           # Architecture and API specifications
├── infra/          # Local environment + deployment manifests
└── .env.example    # Shared environment variable template
```

## Quick Start

1. Copy env vars:

   ```bash
   cp .env.example .env
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start backend + frontend:

   ```bash
   npm run dev
   ```

4. Open:
   - Frontend: <http://localhost:5173>
   - Backend health: <http://localhost:4000/health>

## Scripts

- `npm run dev` - run backend and frontend in parallel
- `npm run build` - build all workspaces
- `npm run lint` - lint all workspaces

## End-to-End Startup Check

After starting both apps:

- Backend should return `{"status":"ok"}` from `/health`
- Frontend shell page displays module sections and backend health status
