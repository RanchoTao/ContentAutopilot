from __future__ import annotations

import hashlib

from .collectors import collect_all
from .config import Settings
from .curator import Curator
from .llm import LLMClient
from .models import Draft, DraftStatus, SafetyStatus
from .queue import QueueStore
from .reviewer import SafetyReviewer
from .writer import XWriter


def _draft_id(event_id: str, text: str) -> str:
    digest = hashlib.sha256(f"{event_id}:{text}".encode("utf-8")).hexdigest()[:16]
    return f"x-{digest}"


class Pipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.store = QueueStore(settings.db_path)

    def collect(self) -> tuple[int, int]:
        events = collect_all(self.settings)
        added = sum(1 for event in events if self.store.upsert_event(event))
        return added, len(events)

    def draft(self) -> tuple[int, int]:
        llm = LLMClient(self.settings)
        curator = Curator(llm)
        writer = XWriter(llm)
        reviewer = SafetyReviewer()

        created = 0
        considered = 0
        for event in self.store.pending_events():
            considered += 1
            curation = curator.evaluate(event)
            if not curation.worth_posting or curation.score < self.settings.min_publish_score:
                self.store.mark_event_processed(event.id)
                continue

            text = writer.write(event, curation)
            safety = reviewer.review(event, text)
            status = DraftStatus.BLOCKED if safety.status == SafetyStatus.BLOCK else DraftStatus.PENDING
            draft = Draft(
                id=_draft_id(event.id, text),
                event_id=event.id,
                text=text,
                status=status,
                safety_status=safety.status,
                safety_reasons=safety.reasons,
                curation_score=curation.score,
            )
            self.store.add_draft(draft)
            self.store.mark_event_processed(event.id)
            created += 1
        return created, considered
