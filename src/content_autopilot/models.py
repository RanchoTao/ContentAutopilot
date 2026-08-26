from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Visibility(StrEnum):
    PUBLIC = "PUBLIC"
    REVIEW = "REVIEW"
    PRIVATE = "PRIVATE"
    EMBARGOED = "EMBARGOED"


class DraftStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"
    BLOCKED = "BLOCKED"


class SafetyStatus(StrEnum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class ContentEvent(BaseModel):
    id: str
    source_type: str
    title: str
    body: str
    occurred_at: datetime
    source_url: str | None = None
    evidence: list[str] = Field(default_factory=list)
    visibility: Visibility = Visibility.REVIEW
    metadata: dict[str, Any] = Field(default_factory=dict)


class CurationResult(BaseModel):
    worth_posting: bool
    score: float = Field(ge=0.0, le=1.0)
    reason: str
    angle: str = ""


class SafetyDecision(BaseModel):
    status: SafetyStatus
    reasons: list[str] = Field(default_factory=list)


class Draft(BaseModel):
    id: str
    event_id: str
    platform: str = "x"
    text: str
    status: DraftStatus = DraftStatus.PENDING
    safety_status: SafetyStatus = SafetyStatus.REVIEW
    safety_reasons: list[str] = Field(default_factory=list)
    curation_score: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: datetime | None = None
    remote_post_id: str | None = None
