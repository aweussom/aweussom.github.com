# Blog ideas

One file per idea, or bullets in `IDEAS.md` — no format police. An idea
graduates by becoming a draft in `content/` (delete or check it off here).

## Google Keep sync

The master capture list lives in Tommy's Google Keep. There is no
official Keep API for personal accounts, the unofficial ones are the
kind of gray zone Google is known to punish (see the agentry post,
lesson 5), and Google's sign-in wall blocks automation-driven browser
profiles — so no browser automation either.

**The protocol: Tommy pastes screenshots of Keep into chat.** Claude
reads them (vision), dedupes against `IDEAS.md`, and merges new entries
under "From Google Keep". Same architecture as the quota-scraper post —
if the vendor won't give you an API, a screenshot and a vision model is
an API.

Keep remains the capture tool (phone-friendly); this folder is the
canonical backlog the blog actually works from.
