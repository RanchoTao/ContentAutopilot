from __future__ import annotations

from pathlib import Path

from .llm import LLMClient
from .models import ContentEvent, CurationResult


DEFAULT_SYSTEM = """Write one X post in English based only on the supplied event and editorial angle.
The author is a researcher-builder. Use a precise, understated, first-person voice.
Do not invent emotions, achievements, affiliations, causal claims, metrics, or future promises.
Prefer concrete observation over generic advice.
No engagement bait. No fake quotations. No emoji unless the source contains them.
Use at most one hashtag, and usually none.
Keep the result at or below 280 characters including any source URL.
Return only the post text.
"""


class XWriter:
    def __init__(self, llm: LLMClient, prompt_path: Path | None = None):
        self.llm = llm
        self.system = DEFAULT_SYSTEM
        if prompt_path and prompt_path.exists():
            self.system = prompt_path.read_text(encoding="utf-8")

    def write(self, event: ContentEvent, curation: CurationResult) -> str:
        source = event.source_url or ""
        user = f"""Editorial angle: {curation.angle}
Event title: {event.title}
Event body: {event.body}
Evidence URL: {source}
"""
        text = self.llm.text(self.system, user, temperature=0.5).strip().strip('"')
        if source and source not in text:
            candidate = f"{text}\n{source}"
            if len(candidate) <= 280:
                text = candidate
        if len(text) > 280:
            raise RuntimeError(f"Generated X draft is {len(text)} characters; refusing to truncate facts")
        return text
