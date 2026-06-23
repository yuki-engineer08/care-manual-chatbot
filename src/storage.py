import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(
    os.environ.get("REPORTS_DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "reports.db"))
)


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submitted_at TEXT NOT NULL,
            fields TEXT NOT NULL,
            reply TEXT NOT NULL
        )
        """
    )
    return conn


def save_report(fields: dict[str, Any], reply: str) -> dict[str, Any]:
    submitted_at = datetime.now(timezone.utc).isoformat()
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO reports (submitted_at, fields, reply) VALUES (?, ?, ?)",
            (submitted_at, json.dumps(fields, ensure_ascii=False), reply),
        )
        conn.commit()
        report_id = cursor.lastrowid
    finally:
        conn.close()
    return {
        "id": report_id,
        "submitted_at": submitted_at,
        "fields": fields,
        "reply": reply,
    }


def list_reports() -> list[dict[str, Any]]:
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT id, submitted_at, fields, reply FROM reports ORDER BY id ASC"
        ).fetchall()
    finally:
        conn.close()
    return [
        {
            "id": row[0],
            "submitted_at": row[1],
            "fields": json.loads(row[2]),
            "reply": row[3],
        }
        for row in rows
    ]
