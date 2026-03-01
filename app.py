import json
import sqlite3
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data.db"
PUBLIC_DIR = BASE_DIR / "public"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              filename TEXT NOT NULL,
              title TEXT NOT NULL,
              tags TEXT,
              description TEXT,
              uploader TEXT NOT NULL,
              category TEXT NOT NULL,
              file_type TEXT NOT NULL,
              uploaded_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_files_uploaded_at ON files(uploaded_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_files_uploader ON files(uploader)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_files_category ON files(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_files_file_type ON files(file_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_files_title ON files(title)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_files_filename ON files(filename)")

        count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        if count == 0:
            seed_data(conn)

        has_fts = True
        try:
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
                  filename, title, tags, description, content='files', content_rowid='id'
                )
                """
            )
            conn.executescript(
                """
                CREATE TRIGGER IF NOT EXISTS files_ai AFTER INSERT ON files BEGIN
                  INSERT INTO files_fts(rowid, filename, title, tags, description)
                  VALUES (new.id, new.filename, new.title, new.tags, new.description);
                END;
                CREATE TRIGGER IF NOT EXISTS files_ad AFTER DELETE ON files BEGIN
                  INSERT INTO files_fts(files_fts, rowid, filename, title, tags, description)
                  VALUES ('delete', old.id, old.filename, old.title, old.tags, old.description);
                END;
                CREATE TRIGGER IF NOT EXISTS files_au AFTER UPDATE ON files BEGIN
                  INSERT INTO files_fts(files_fts, rowid, filename, title, tags, description)
                  VALUES ('delete', old.id, old.filename, old.title, old.tags, old.description);
                  INSERT INTO files_fts(rowid, filename, title, tags, description)
                  VALUES (new.id, new.filename, new.title, new.tags, new.description);
                END;
                """
            )
            conn.execute("INSERT INTO files_fts(files_fts) VALUES ('rebuild')")
        except sqlite3.OperationalError:
            has_fts = False

        conn.execute(
            "CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO app_meta(key, value) VALUES('search_mode', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("full-text" if has_fts else "like-fallback",),
        )


def seed_data(conn):
    rows = [
        (
            "quarterly_finance_q1.pdf",
            "Q1 Finance Summary",
            "finance,quarterly,board",
            "Executive quarterly financial report for Q1.",
            "maya",
            "finance",
            "pdf",
            "2025-01-15",
        ),
        (
            "onboarding-checklist-v2.docx",
            "Employee Onboarding Checklist",
            "hr,onboarding,policy",
            "Latest onboarding checklist for new hires.",
            "liam",
            "hr",
            "docx",
            "2025-02-03",
        ),
        (
            "vendor-contract-template.docx",
            "Vendor Contract Template",
            "legal,contract,template",
            "Approved contract template for procurement vendors.",
            "emma",
            "legal",
            "docx",
            "2024-12-22",
        ),
        (
            "incident-postmortem-0425.md",
            "Incident Postmortem 04/25",
            "engineering,incident,infra",
            "Root cause analysis and remediation steps.",
            "noah",
            "engineering",
            "md",
            "2025-04-28",
        ),
        (
            "marketing-launch-plan.pptx",
            "Spring Launch Plan",
            "marketing,campaign,launch",
            "Go-to-market presentation for spring launch.",
            "ava",
            "marketing",
            "pptx",
            "2025-03-11",
        ),
    ]
    conn.executemany(
        """
        INSERT INTO files(filename, title, tags, description, uploader, category, file_type, uploaded_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )


def search_files(params):
    q = params.get("q", [""])[0].strip()
    date_from = params.get("dateFrom", [""])[0]
    date_to = params.get("dateTo", [""])[0]
    uploader = params.get("uploader", [""])[0]
    category = params.get("category", [""])[0]
    file_type = params.get("fileType", [""])[0]
    sort = params.get("sort", ["relevance"])[0]

    with get_conn() as conn:
        search_mode = conn.execute(
            "SELECT value FROM app_meta WHERE key='search_mode'"
        ).fetchone()[0]

        where = []
        sql_params = []

        def add_filter(clause, value):
            if value:
                where.append(clause)
                sql_params.append(value)

        add_filter("uploaded_at >= ?", date_from)
        add_filter("uploaded_at <= ?", date_to)
        add_filter("uploader = ?", uploader)
        add_filter("category = ?", category)
        add_filter("file_type = ?", file_type)

        if search_mode == "full-text" and q:
            where.insert(0, "files_fts MATCH ?")
            sql_params.insert(0, q)

            order_by = {
                "date": "uploaded_at DESC",
                "name": "title COLLATE NOCASE ASC",
                "relevance": "relevance_score ASC",
            }.get(sort, "relevance_score ASC")

            sql = f"""
              SELECT files.*, bm25(files_fts, 1.2, 1.0, 0.8, 0.8) AS relevance_score
              FROM files_fts JOIN files ON files.id = files_fts.rowid
              {'WHERE ' + ' AND '.join(where) if where else ''}
              ORDER BY {order_by}
              LIMIT 100
            """
            rows = conn.execute(sql, sql_params).fetchall()
        else:
            if q:
                like = f"%{q}%"
                where.append("""(
                  filename LIKE ? COLLATE NOCASE OR
                  title LIKE ? COLLATE NOCASE OR
                  tags LIKE ? COLLATE NOCASE OR
                  description LIKE ? COLLATE NOCASE
                )""")
                sql_params.extend([like, like, like, like])

            order_by = "uploaded_at DESC"
            if sort == "name":
                order_by = "title COLLATE NOCASE ASC"
            elif sort == "relevance" and q:
                like = f"%{q}%"
                order_by = """
                (
                  (CASE WHEN filename LIKE ? COLLATE NOCASE THEN 4 ELSE 0 END) +
                  (CASE WHEN title LIKE ? COLLATE NOCASE THEN 3 ELSE 0 END) +
                  (CASE WHEN tags LIKE ? COLLATE NOCASE THEN 2 ELSE 0 END) +
                  (CASE WHEN description LIKE ? COLLATE NOCASE THEN 1 ELSE 0 END)
                ) DESC,
                uploaded_at DESC
                """
                sql_params.extend([like, like, like, like])

            sql = f"""
              SELECT *, 0 as relevance_score
              FROM files
              {'WHERE ' + ' AND '.join(where) if where else ''}
              ORDER BY {order_by}
              LIMIT 100
            """
            rows = conn.execute(sql, sql_params).fetchall()

    return {
        "results": [dict(r) for r in rows],
        "total": len(rows),
        "searchMode": search_mode,
    }


def get_filters():
    with get_conn() as conn:
        uploaders = [r[0] for r in conn.execute("SELECT DISTINCT uploader FROM files ORDER BY uploader")]
        categories = [r[0] for r in conn.execute("SELECT DISTINCT category FROM files ORDER BY category")]
        file_types = [r[0] for r in conn.execute("SELECT DISTINCT file_type FROM files ORDER BY file_type")]
    return {"uploaders": uploaders, "categories": categories, "fileTypes": file_types}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def _json(self, data, code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/search":
            self._json(search_files(parse_qs(parsed.query)))
            return
        if parsed.path == "/api/filters":
            self._json(get_filters())
            return
        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_GET()


def run_server(port=3000):
    init_db()
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Server listening on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
