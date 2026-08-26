from __future__ import annotations

import re

from .models import ContentEvent, SafetyDecision, SafetyStatus, Visibility


SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("OpenAI-style secret", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]

BLOCK_MARKERS = (
    "do not publish",
    "do-not-publish",
    "confidential",
    "private only",
    "under embargo",
)


class SafetyReviewer:
    def review(self, event: ContentEvent, text: str) -> SafetyDecision:
        reasons: list[str] = []

        if event.visibility in {Visibility.PRIVATE, Visibility.EMBARGOED}:
            return SafetyDecision(
                status=SafetyStatus.BLOCK,
                reasons=[f"Source visibility is {event.visibility.value}"],
            )

        combined = f"{event.title}\n{event.body}\n{text}"
        lowered = combined.lower()

        for label, pattern in SECRET_PATTERNS:
            if pattern.search(combined):
                reasons.append(f"Possible secret detected: {label}")

        for marker in BLOCK_MARKERS:
            if marker in lowered:
                reasons.append(f"Publication-blocking marker detected: {marker}")

        if reasons:
            return SafetyDecision(status=SafetyStatus.BLOCK, reasons=reasons)

        if not event.evidence and not event.source_url:
            return SafetyDecision(
                status=SafetyStatus.REVIEW,
                reasons=["No external evidence URL; human verification required"],
            )

        if event.visibility == Visibility.REVIEW:
            return SafetyDecision(
                status=SafetyStatus.REVIEW,
                reasons=["Source visibility requires human review"],
            )

        return SafetyDecision(status=SafetyStatus.PASS, reasons=[])
