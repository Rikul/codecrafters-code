from __future__ import annotations

from datetime import datetime, timedelta
from .app_logging import log
from .config import APP_DB
import sqlite3
import asyncio
from .helper_agent import HelperAgent


TASKS_SYSTEM_PROMPT = """
You are a background agent running periodic tasks. The user is not present.
Read your instructions and execute them. Be concise.
"""

class ScheduledTasks:
    def __init__(self):
        self._init_tasks_db()

    def _init_tasks_db(self):
        with sqlite3.connect(APP_DB) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    name            TEXT    NOT NULL UNIQUE,
                    prompt          TEXT    NOT NULL,
                    enabled         INTEGER NOT NULL DEFAULT 1,
                    created_at      TEXT    NOT NULL,
                    interval_mins   INTEGER NOT NULL DEFAULT 1,
                    last_run        TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_outputs (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    name         TEXT    NOT NULL,
                    prompt       TEXT    NOT NULL,
                    output       TEXT    NOT NULL,
                    timestamp    TEXT    NOT NULL
                )
            """)
            conn.commit()


    def load_tasks(self) -> list[dict]:
        query = "SELECT name, prompt, enabled, created_at, interval_mins, last_run FROM tasks"
        with sqlite3.connect(APP_DB) as conn:
            rows = conn.execute(query).fetchall()

        return [{"name": n, "prompt": p, "enabled": e, "created_at": c, "interval_mins": i, "last_run": r}
                for n, p, e, c, i, r in rows]


    def add_task(self, name: str, prompt: str, interval_mins: int = 1):
        with sqlite3.connect(APP_DB) as conn:
            try:
                conn.execute("""
                    INSERT INTO tasks (name, prompt, interval_mins, created_at)
                    VALUES (?, ?, ?, ?)
                """, (name, prompt, interval_mins, datetime.now().isoformat()))
                conn.commit()
            except sqlite3.IntegrityError:
                raise ValueError(f"Task '{name}' already exists")
    
    def remove_task(self, name: str):
        with sqlite3.connect(APP_DB) as conn:
            conn.execute("DELETE FROM tasks WHERE name = ?", (name,))
            conn.commit()

    def enable_task(self, name: str):
        with sqlite3.connect(APP_DB) as conn:
            conn.execute("UPDATE tasks SET enabled = 1 WHERE name = ?", (name,))
            conn.commit()

    def disable_task(self, name: str):
        with sqlite3.connect(APP_DB) as conn:
            conn.execute("UPDATE tasks SET enabled = 0 WHERE name = ?", (name,))
            conn.commit()


    def save_output(self, name: str, prompt: str, output: str):
        with sqlite3.connect(APP_DB) as conn:
            conn.execute("""
                INSERT INTO task_outputs (name, prompt, output, timestamp)
                VALUES (?, ?, ?, ?)
            """, (name, prompt, output, datetime.now().isoformat()))
            conn.commit()

    def get_output(self, name: str, num_entries: int = 5) -> list[dict]:
        with sqlite3.connect(APP_DB) as conn:
            rows = conn.execute("""
                SELECT prompt, output, timestamp FROM task_outputs
                WHERE name = ?
                ORDER BY id DESC LIMIT ?
            """, (name, num_entries)).fetchall()
        return [{"prompt": p, "output": o, "timestamp": t} for p, o, t in reversed(rows)]
    
    def _update_last_run(self, name: str, ts: str):
        with sqlite3.connect(APP_DB) as conn:
            conn.execute("UPDATE tasks SET last_run = ? WHERE name = ?", (ts, name))
            conn.commit()

    def _is_due(self, task: dict, now: datetime) -> bool:
        baseline = task["last_run"] or task["created_at"]
        last = datetime.fromisoformat(baseline)
        return (now - last) >= timedelta(minutes=task["interval_mins"])

    async def run_task(self, name: str, prompt: str) -> str:
        log.info(f"Running scheduled task '{name}'")
        agent = HelperAgent(system_prompt=TASKS_SYSTEM_PROMPT)
        output = await agent.agent_loop(prompt)
        ts = datetime.now().isoformat()
        self.save_output(name=name, prompt=prompt, output=output)
        self._update_last_run(name=name, ts=ts)
        return output

    async def run(self):
        while True:
            now = datetime.now()
            tasks = self.load_tasks()
            due = [t for t in tasks if t["enabled"] and self._is_due(t, now)]
            if due:
                await asyncio.gather(*[self.run_task(t["name"], t["prompt"]) for t in due])
            await asyncio.sleep(60)