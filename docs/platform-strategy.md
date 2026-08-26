# Platform strategy

ContentAutopilot should adapt one real event to the audience and grammar of each platform rather than spray identical text everywhere.

| Platform | Role | Intended automation |
|---|---|---|
| X | Academic/technical updates and external connection | High; first full API integration |
| Zhihu | Deep Chinese explanations and answers | AI discovery + drafting; publication only through supported mechanisms |
| Xiaohongshu | Work/life records, photos, short videos | AI selection, captioning and packaging; preserve real-life source media |
| WeChat Official Account | Public updates for personal ventures + essays | Drafting/editorial assistance, lower cadence |
| Personal site | Canonical academic record and essays | High for structured updates |
| Bilibili | Deep project/research video | Low-to-medium; AI assists scripting, packaging and clipping |
| Douyin | Dense short-form derivatives and visual demos | Medium; derive from real long-form/source material |
| YouTube | International long-form research/builder content | Low-to-medium; reuse or translate selected deep content |
| GitHub / arXiv / Hugging Face / ORCID | Open-source and academic infrastructure | Not treated as social-media posting targets |

## Current priority

1. X end-to-end loop.
2. Analytics feedback.
3. Review UI.
4. Zhihu discovery/drafting.
5. Xiaohongshu media-aware drafting.
6. Cross-platform scheduling and transformation.

Do not add a platform adapter merely because an unofficial browser automation can click its publish button. Prefer supported APIs and explicit permissions.