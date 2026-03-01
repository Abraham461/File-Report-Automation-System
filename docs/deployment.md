# FRAS Deployment Guide

This guide is aligned to the Python/FastAPI service in this repository (`app/main.py`) and its Alembic migrations.

## 1) Environment setup

### Prerequisites
- Linux server or container runtime (Ubuntu 22.04+ recommended)
- Python 3.11+
- PostgreSQL 14+ (production) or SQLite (local/dev)
- Reverse proxy (Nginx/Caddy)
- Git

### Clone project
```bash
git clone <your-repo-url> fras
cd fras
```

### Create environment variables
Create `.env` at project root:
```env
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
APP_SECRET=<replace-with-long-random-secret>
DATABASE_URL=postgresql://fras_user:<password>@localhost:5432/fras_db
LOG_LEVEL=INFO
```

### Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 2) Database migration

### Create database and user (PostgreSQL)
```sql
CREATE USER fras_user WITH PASSWORD '<password>';
CREATE DATABASE fras_db OWNER fras_user;
GRANT ALL PRIVILEGES ON DATABASE fras_db TO fras_user;
```

### Run migrations (Alembic)
```bash
alembic upgrade head
```

### Seed baseline data (optional)
```bash
python scripts/seed.py
```

## 3) Production run steps

### Start application process
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### Configure reverse proxy (Nginx snippet)
```nginx
server {
    listen 80;
    server_name fras.example.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Run as service (systemd)
```ini
[Unit]
Description=FRAS Service
After=network.target

[Service]
User=fras
WorkingDirectory=/opt/fras
EnvironmentFile=/opt/fras/.env
ExecStart=/opt/fras/.venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fras
sudo systemctl start fras
sudo systemctl status fras
```

## 4) Post-deployment verification

```bash
curl -sSf http://127.0.0.1:8000/health
curl -sSf http://127.0.0.1:8000/api/report-templates
curl -sSf http://127.0.0.1:8000/api/reports/history
```

## 5) Backup and recovery
- Database backup: nightly `pg_dump` to secure storage.
- Keep at least 14 days of restore points.
