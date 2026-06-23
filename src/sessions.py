import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(
    os.environ.get("SESSIONS_DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "sessions.db"))
)


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS revoked_sessions (
            session_id TEXT PRIMARY KEY,
            revoked_at TEXT NOT NULL
        )
        """
    )
    return conn


def revoke_session(session_id: str) -> None:
    revoked_at = datetime.now(timezone.utc).isoformat()
    conn = _get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO revoked_sessions (session_id, revoked_at) VALUES (?, ?)",
            (session_id, revoked_at),
        )
        conn.commit()
    finally:
        conn.close()


def is_session_revoked(session_id: str) -> bool:
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM revoked_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    finally:
        conn.close()
    return row is not None
