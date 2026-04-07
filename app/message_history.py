from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from .app_logging import log
from .config import APP_NAME

HISTORY_DB = Path.home() / f".{APP_NAME}" / "history.db"

class MessageHistory:
    def __init__(self, channel_type: str, db_path: Path = HISTORY_DB):
        self.db_path = db_path
        self.channel = channel_type
        self._ensure_db()

    def _ensure_db(self):
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channel text NOT NULL,
                        dir text,
                        project text,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel)
                """)
                conn.commit()
        
        except sqlite3.Error as e:
            log.error(f"Error creating message history database: {str(e)}")
            raise

    def add_message(self, role: str, content: str, dir: str | None = None, project: str | None = None):
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (channel, role, content, timestamp, dir, project) VALUES (?, ?, ?, ?, ?, ?)",
                (self.channel, role, content, timestamp, dir, project)
            )
            conn.commit()
        log.info(f"Added message to history: role={role}, content={content[:30]}...")

    def get_history(self, limit: int = 100) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""SELECT role, content, timestamp FROM messages
                                    where channel = ?
                                    ORDER BY id desc limit ?""", (self.channel, limit)).fetchall()
            return [{"role": row[0], "content": row[1]} for row in reversed(rows)]
        
    def prune_old_messages(self, older_than_days: int) -> None:
        pass