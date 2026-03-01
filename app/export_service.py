"""Export services for report outputs."""

from __future__ import annotations

from pathlib import Path

EXPORT_DIR = Path("storage/exports")


def ensure_export_dir() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def export_to_pdf(report_id: str, report_text: str) -> Path:
    ensure_export_dir()
    filepath = EXPORT_DIR / f"{report_id}.pdf"

    lines = report_text.split("\n")
    commands = ["BT", "/F1 11 Tf", "40 800 Td"]

    for index, line in enumerate(lines):
        if index > 0:
            commands.append("0 -14 Td")
        commands.append(f"({escape_pdf_text(line)}) Tj")

    commands.append("ET")
    stream = "\n".join(commands)

    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj",
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
        f"5 0 obj << /Length {len(stream)} >> stream\n{stream}\nendstream endobj",
    ]

    pdf = "%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf.encode("latin-1")))
        pdf += f"{obj}\n"

    xref_start = len(pdf.encode("latin-1"))
    pdf += f"xref\n0 {len(objects) + 1}\n"
    pdf += "0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{str(offset).zfill(10)} 00000 n \n"
    pdf += f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF"

    filepath.write_bytes(pdf.encode("latin-1"))
    return filepath
