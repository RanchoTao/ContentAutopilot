from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

from .config import Settings
from .models import ContentEvent, Visibility


def _stable_id(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


class GitHubCollector:
    def __init__(self, settings: Settings):
        self.settings = settings

    def collect(self) -> list[ContentEvent]:
        if not self.settings.watched_repos:
            return []

        headers = {"Accept": "application/vnd.github+json"}
        if self.settings.github_token:
            headers["Authorization"] = f"Bearer {self.settings.github_token}"

        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.settings.lookback_hours)
        events: list[ContentEvent] = []

        with httpx.Client(headers=headers, timeout=20) as client:
            for repo in self.settings.watched_repos:
                response = client.get(
                    f"https://api.github.com/repos/{repo}/commits",
                    params={"since": cutoff.isoformat(), "per_page": 50},
                )
                response.raise_for_status()
                for item in response.json():
                    commit = item.get("commit", {})
                    message = (commit.get("message") or "").strip()
                    if not message:
                        continue
                    date_raw = (
                        commit.get("committer", {}).get("date")
                        or commit.get("author", {}).get("date")
                    )
                    occurred_at = (
                        datetime.fromisoformat(date_raw.replace("Z", "+00:00"))
                        if date_raw
                        else datetime.now(timezone.utc)
                    )
                    url = item.get("html_url")
                    sha = item.get("sha", "")
                    title = message.splitlines()[0][:180]
                    events.append(
                        ContentEvent(
                            id=f"gh-{_stable_id(repo + sha)}",
                            source_type="github_commit",
                            title=title,
                            body=message,
                            occurred_at=occurred_at,
                            source_url=url,
                            evidence=[url] if url else [],
                            visibility=Visibility.REVIEW,
                            metadata={"repo": repo, "sha": sha},
                        )
                    )
        return events


class ManualNoteCollector:
    def __init__(self, inbox_dir: Path):
        self.inbox_dir = inbox_dir

    def collect(self) -> list[ContentEvent]:
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        events: list[ContentEvent] = []
        for path in sorted(self.inbox_dir.glob("*.md")):
            raw = path.read_text(encoding="utf-8").strip()
            if not raw:
                continue
            visibility, source_url, body = self._parse_metadata(raw)
            stat = path.stat()
            occurred_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            title = next((line.strip("# ") for line in body.splitlines() if line.strip()), path.stem)
            evidence = [source_url] if source_url else []
            events.append(
                ContentEvent(
                    id=f"note-{_stable_id(str(path.resolve()) + raw)}",
                    source_type="manual_note",
                    title=title[:180],
                    body=body,
                    occurred_at=occurred_at,
                    source_url=source_url,
                    evidence=evidence,
                    visibility=visibility,
                    metadata={"path": str(path)},
                )
            )
        return events

    @staticmethod
    def _parse_metadata(raw: str) -> tuple[Visibility, str | None, str]:
        visibility = Visibility.REVIEW
        source_url: str | None = None
        lines = raw.splitlines()
        body_start = 0
        for index, line in enumerate(lines[:8]):
            stripped = line.strip()
            if not stripped:
                body_start = index + 1
                break
            if stripped.lower().startswith("visibility:"):
                value = stripped.split(":", 1)[1].strip().upper()
                try:
                    visibility = Visibility(value)
                except ValueError:
                    visibility = Visibility.REVIEW
                body_start = index + 1
            elif stripped.lower().startswith("source_url:"):
                source_url = stripped.split(":", 1)[1].strip() or None
                body_start = index + 1
            else:
                break
        return visibility, source_url, "\n".join(lines[body_start:]).strip() or raw


def collect_all(settings: Settings) -> list[ContentEvent]:
    return GitHubCollector(settings).collect() + ManualNoteCollector(settings.inbox_dir).collect()
