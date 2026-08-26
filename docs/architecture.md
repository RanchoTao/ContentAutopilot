# Architecture

## Objective

ContentAutopilot is a personal public-information layer. It watches real work, extracts publishable signals, transforms them for a platform, and keeps a human at the final publication boundary.

The important distinction is between **automation of editorial labor** and **automation of identity**. The former is useful; the latter is dangerous. Models can summarize, select, rewrite and schedule. They may not manufacture a life for the user.

## Components

### 1. Collectors

Collectors produce `ContentEvent` objects with source type, timestamp, body, visibility and evidence. The MVP supports:

- recent commits from configured GitHub repositories;
- Markdown notes dropped into `data/inbox/`.

Later collectors can read release notes, personal-site posts, arXiv releases, experiment logs, newsletters, calendar events explicitly marked public, or company changelogs.

### 2. Curator

The curator answers one question: **is this worth making public?**

It assigns a score and an editorial angle. A minimum score prevents a posting quota from degenerating into filler. Private and embargoed events are rejected before model reasoning.

### 3. Platform writer

Each platform needs its own writer. The MVP has only `XWriter`; cross-posting the same text everywhere is explicitly not the target architecture.

### 4. Safety reviewer

The first reviewer is deterministic and intentionally conservative. It blocks common credential patterns and publication markers, respects source visibility, and escalates unsupported evidence to human review.

A later version may add a second LLM-based factual-diff reviewer, but deterministic guards remain mandatory.

### 5. Queue

SQLite stores collected events and generated drafts. Drafts move through:

```text
PENDING -> APPROVED -> PUBLISHED
       \-> REJECTED
BLOCKED (terminal until source/policy changes)
```

Approval is a deliberate human action.

### 6. Publisher

The X adapter accepts only approved drafts. Live publishing requires both the CLI `--live` flag and an environment-level allow switch. This two-key design prevents an accidental command from becoming a public post.

## Near-term architecture decisions

- Keep scheduling separate from curation. A scheduler may decide *when* to publish, not *what facts are true*.
- Keep platform adapters isolated so policy/API changes do not contaminate the core pipeline.
- Store provenance for every draft. A future UI should make source evidence one click away.
- Optimize for trust and signal density before growth metrics.
