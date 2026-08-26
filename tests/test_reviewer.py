from datetime import datetime, timezone

from content_autopilot.models import ContentEvent, SafetyStatus, Visibility
from content_autopilot.reviewer import SafetyReviewer


def event(**kwargs):
    base = dict(
        id="e1",
        source_type="manual_note",
        title="A real result",
        body="Released a small benchmark result.",
        occurred_at=datetime.now(timezone.utc),
        source_url="https://example.com/evidence",
        evidence=["https://example.com/evidence"],
        visibility=Visibility.PUBLIC,
    )
    base.update(kwargs)
    return ContentEvent(**base)


def test_public_evidenced_event_passes():
    result = SafetyReviewer().review(event(), "A small benchmark result is now available.")
    assert result.status == SafetyStatus.PASS


def test_embargo_blocks():
    result = SafetyReviewer().review(
        event(visibility=Visibility.EMBARGOED),
        "Preliminary result.",
    )
    assert result.status == SafetyStatus.BLOCK


def test_secret_blocks():
    result = SafetyReviewer().review(
        event(body="Temporary credential sk-abcdefghijklmnopqrstuvwxyz123456"),
        "Debugging an API integration.",
    )
    assert result.status == SafetyStatus.BLOCK


def test_no_evidence_requires_review():
    result = SafetyReviewer().review(
        event(source_url=None, evidence=[]),
        "A personal observation from today.",
    )
    assert result.status == SafetyStatus.REVIEW
