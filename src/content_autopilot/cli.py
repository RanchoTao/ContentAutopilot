from __future__ import annotations

from datetime import datetime, timezone

import typer
from rich.console import Console
from rich.table import Table

from .config import load_settings
from .models import DraftStatus
from .pipeline import Pipeline
from .publisher_x import XPublisher
from .queue import QueueStore

app = typer.Typer(no_args_is_help=True, help="Evidence-first AI content operations")
console = Console()


def _store() -> tuple[QueueStore, object]:
    settings = load_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.inbox_dir.mkdir(parents=True, exist_ok=True)
    return QueueStore(settings.db_path), settings


@app.command("init-data")
def init_data() -> None:
    """Create local data directories and initialize the SQLite queue."""
    store, settings = _store()
    _ = store
    console.print(f"Initialized [bold]{settings.data_dir}[/bold]")


@app.command()
def collect() -> None:
    """Collect new evidence from configured sources."""
    settings = load_settings()
    pipeline = Pipeline(settings)
    added, seen = pipeline.collect()
    console.print(f"Collected {seen} event(s); {added} new.")


@app.command()
def draft() -> None:
    """Curate pending events and create X drafts."""
    settings = load_settings()
    pipeline = Pipeline(settings)
    created, considered = pipeline.draft()
    console.print(f"Considered {considered} event(s); created {created} draft(s).")


@app.command("queue")
def show_queue(status: DraftStatus | None = typer.Option(None, case_sensitive=False)) -> None:
    """Show the review queue."""
    store, _ = _store()
    drafts = store.list_drafts(status=status)
    table = Table(title="ContentAutopilot review queue")
    table.add_column("ID", no_wrap=True)
    table.add_column("Status")
    table.add_column("Safety")
    table.add_column("Score")
    table.add_column("Text")
    for item in drafts:
        table.add_row(
            item.id,
            item.status.value,
            item.safety_status.value,
            f"{item.curation_score:.2f}",
            item.text,
        )
    console.print(table)


@app.command()
def approve(draft_id: str) -> None:
    """Explicitly approve a draft for possible live publishing."""
    store, _ = _store()
    draft = store.approve(draft_id)
    console.print(f"Approved {draft.id}")


@app.command()
def reject(draft_id: str) -> None:
    """Reject a draft."""
    store, _ = _store()
    draft = store.reject(draft_id)
    console.print(f"Rejected {draft.id}")


@app.command()
def publish(
    live: bool = typer.Option(False, "--live", help="Actually call the X API."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print approved posts without publishing."),
) -> None:
    """Publish approved drafts. Live mode requires an environment safety switch too."""
    store, settings = _store()
    approved = store.list_drafts(DraftStatus.APPROVED)
    if not approved:
        console.print("No approved drafts.")
        return

    if not live or dry_run:
        for item in approved:
            console.print(f"[bold]{item.id}[/bold]\n{item.text}\n")
        console.print("Dry run only. Nothing was published.")
        return

    if not settings.allow_live_publish:
        raise typer.BadParameter(
            "Live publishing is disabled. Set CONTENTAUTOPILOT_ALLOW_LIVE_PUBLISH=true first."
        )

    publisher = XPublisher(settings)
    for item in approved:
        remote_id = publisher.publish(item.text)
        item.status = DraftStatus.PUBLISHED
        item.remote_post_id = remote_id
        item.published_at = datetime.now(timezone.utc)
        store.save_draft(item)
        console.print(f"Published {item.id} -> X post {remote_id}")


@app.command()
def run() -> None:
    """Run the safe local loop: collect evidence, then create reviewable drafts."""
    settings = load_settings()
    pipeline = Pipeline(settings)
    added, seen = pipeline.collect()
    created, considered = pipeline.draft()
    console.print(
        f"Collected {seen} ({added} new); considered {considered}; created {created} draft(s)."
    )
