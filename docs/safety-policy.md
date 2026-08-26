# Safety and publication policy

## Visibility levels

| Level | Meaning | Default action |
|---|---|---|
| `PUBLIC` | Explicitly safe for public use | May proceed through automated checks |
| `REVIEW` | Public intent is not certain | Human approval required |
| `PRIVATE` | Personal/internal material | Block |
| `EMBARGOED` | Temporarily restricted research or company information | Block |

Collectors should prefer `REVIEW` unless a source explicitly establishes public status.

## Evidence rule

A publishable factual statement should be traceable to a source event. If a model needs to invent connective facts to make a draft interesting, the event is not ready to publish.

## Research rule

Unreleased ideas, preliminary experiments, reviewer correspondence, private collaborator discussions, unpublished benchmarks and submission-sensitive results are not public merely because the local system can read them.

## Credentials and operational data

Never publish API keys, tokens, private keys, cookies, internal hostnames, private repositories, server credentials, unreleased security findings, or personal contact details.

## Growth rule

The system must not optimize engagement by fabricating controversy, impersonating other people, mass-replying, following/unfollowing, or generating repetitive low-information posts.

## Human boundary

The author remains responsible for the public claim. The MVP therefore requires explicit approval before live publishing even when deterministic safety checks pass.
