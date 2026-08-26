# ContentAutopilot

> AI-assisted personal media operations for researchers and builders.

ContentAutopilot turns real work into publishable updates without letting an LLM invent a fake public persona. It collects evidence from GitHub and a local inbox, decides whether an event is worth sharing, writes platform-specific drafts, runs safety checks, puts drafts into a review queue, and only publishes after explicit approval.

## Design principles

- **Evidence first** — no evidence, no post.
- **Human identity** — the model may rewrite your work, but may not invent experiences, opinions, results, affiliations, or achievements.
- **Privacy by default** — uncertain material goes to review, not publication.
- **Research embargo** — unpublished or embargoed research is blocked unless explicitly released.
- **Quality over frequency** — silence is better than filler.
- **Human approval before live publishing** — the MVP never publishes an unapproved draft.

## MVP scope

The first usable loop is intentionally narrow:

```text
GitHub commits / manual notes
            ↓
        collectors
            ↓
      AI curation
            ↓
       X drafting
            ↓
 deterministic safety checks
            ↓
       review queue
            ↓
  explicit human approval
            ↓
      X API publishing
```

Zhihu, Xiaohongshu, WeChat Official Accounts, Bilibili, Douyin and YouTube are later adapters. The project should prove the loop on X before multiplying integrations.

## Quick start

Requirements: Python 3.11+.

```bash
git clone https://github.com/RanchoTao/ContentAutopilot.git
cd ContentAutopilot
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Configure at least one content source and an OpenAI-compatible model endpoint in `.env`, then:

```bash
content-autopilot init-data
content-autopilot collect
content-autopilot draft
content-autopilot queue
content-autopilot approve <draft-id>
content-autopilot publish --dry-run
```

Live publishing is deliberately guarded by two switches. You must set `CONTENTAUTOPILOT_ALLOW_LIVE_PUBLISH=true` **and** invoke:

```bash
content-autopilot publish --live
```

## Manual notes

Drop Markdown files into `data/inbox/`. A note can optionally start with simple metadata:

```md
visibility: REVIEW
source_url: https://example.com/evidence

Ran experiment X across five seeds. The failure mode appears to be ...
```

Allowed visibility values are `PUBLIC`, `REVIEW`, `PRIVATE`, and `EMBARGOED`.

## Configuration

See `.env.example`. LLM access is provider-agnostic as long as the endpoint supports the OpenAI-compatible Chat Completions API.

For X publishing, the MVP uses user-context credentials through Tweepy. Never commit credentials. Keep the repository private if you later add personal data, internal feeds, unreleased research notes, or company information.

## Project structure

```text
src/content_autopilot/
  collectors.py       # GitHub + local Markdown evidence
  config.py           # environment settings
  curator.py          # decide what deserves a post
  llm.py              # OpenAI-compatible client
  models.py           # event/draft schemas
  pipeline.py         # end-to-end orchestration
  publisher_x.py      # X adapter
  queue.py            # SQLite persistence + review queue
  reviewer.py         # deterministic publication guardrails
  writer.py           # X-specific writing
  cli.py              # command line interface
prompts/               # editable agent policies
docs/                  # architecture, platform strategy, safety
```

## Roadmap

1. Prove the X loop locally with human approval.
2. Add analytics and post-performance feedback.
3. Add a lightweight review dashboard.
4. Add read-only discovery for Zhihu and Xiaohongshu; keep publishing manual until a supported API/permission exists.
5. Add cross-platform content transforms.
6. Add scheduling and cadence control.
7. Add a learning loop that optimizes topic selection without optimizing for spam.

## Status

Early MVP scaffold. Safe-by-default and intentionally conservative.