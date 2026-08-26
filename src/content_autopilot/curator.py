from __future__ import annotations

from pathlib import Path

from .llm import LLMClient
from .models import ContentEvent, CurationResult, Visibility


DEFAULT_SYSTEM = """You are a conservative editor for a researcher's public account.
Decide whether a real event is worth sharing on X.
Prefer concrete results, useful lessons, released artifacts, non-obvious failures, and specific observations.
Reject routine commits, filler, vague motivation, unsupported claims, status theater, and anything that would require inventing facts.
The event's evidence is authoritative. Do not add facts not present in the event.
Return JSON with: worth_posting (boolean), score (0..1), reason (string), angle (string).
"""


class Curator:
    def __init__(self, llm: LLMClient, prompt_path: Path | None = None):
        self.llm = llm
        self.system = DEFAULT_SYSTEM
        if prompt_path and prompt_path.exists():
            self.system = prompt_path.read_text(encoding="utf-8")

    def evaluate(self, event: ContentEvent) -> CurationResult:
        if event.visibility in {Visibility.PRIVATE, Visibility.EMBARGOED}:
            return CurationResult(
                worth_posting=False,
                score=0.0,
                reason=f"Visibility is {event.visibility.value}",
                angle="",
            )

        payload = event.model_dump_json(indent=2)
        data = self.llm.json(self.system, payload)
        return CurationResult.model_validate(data)
