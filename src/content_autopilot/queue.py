from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import ContentEvent, Draft, DraftStatus


class QueueStore:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    processed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS drafts (
                    id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(event_id) REFERENCES events(id)
                );
                """
            )

    def upsert_event(self, event: ContentEvent) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO events(id, payload, processed, created_at) VALUES(?, ?, 0, ?)",
                (event.id, event.model_dump_json(), datetime.now(timezone.utc).isoformat()),
            )
            return cursor.rowcount > 0

    def pending_events(self) -> list[ContentEvent]:
        with self._connect() as conn:
            rows = conn.execute("SELECT payload FROM events WHERE processed = 0 ORDER BY created_at").fetchall()
        return [ContentEvent.model_validate_json(row["payload"]) for row in rows]

    def mark_event_processed(self, event_id: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE events SET processed = 1 WHERE id = ?", (event_id,))

    def add_draft(self, draft: Draft) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO drafts(id, event_id, payload, status, created_at) VALUES(?, ?, ?, ?, ?)",
                (
                    draft.id,
                    draft.event_id,
                    draft.model_dump_json(),
                    draft.status.value,
                    draft.created_at.isoformat(),
                ),
            )

    def list_drafts(self, status: DraftStatus | None = None) -> list[Draft]:
        query = "SELECT payload FROM drafts"
        params: tuple[str, ...] = ()
        if status is not None:
            query += " WHERE status = ?"
            params = (status.value,)
        query += " ORDER BY created_at DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [Draft.model_validate_json(row["payload"]) for row in rows]

    def get_draft(self, draft_id: str) -> Draft | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        return Draft.model_validate_json(row["payload"]) if row else None

    def save_draft(self, draft: Draft) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE drafts SET payload = ?, status = ? WHERE id = ?",
                (draft.model_dump_json(), draft.status.value, draft.id),
            )

    def approve(self, draft_id: str) -> Draft:
        draft = self.get_draft(draft_id)
        if not draft:
            raise KeyError(draft_id)
        if draft.status == DraftStatus.BLOCKED:
            raise ValueError("Blocked drafts cannot be approved")
        draft.status = DraftStatus.APPROVED
        self.save_draft(draft)
        return draft

    def reject(self, draft_id: str) -> Draft:
        draft = self.get_draft(draft_id)
        if not draft:
            raise KeyError(draft_id)
        draft.status = DraftStatus.REJECTED
        self.save_draft(draft)
        return draft
