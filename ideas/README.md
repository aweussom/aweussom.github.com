# Blog ideas

One file per idea, or bullets in `IDEAS.md` — no format police. An idea
graduates by becoming a draft in `content/` (delete or check it off here).

## Google Keep sync

The master capture list lives in Tommy's Google Keep. There is no
official Keep API for personal accounts, and the unofficial ones are the
kind of gray zone Google is known to punish (see the agentry post,
lesson 5). The sanctioned route:

- Claude reads keep.google.com through the chrome-devtools browser —
  Tommy's own logged-in session, no stored credentials, no third-party
  API. Ask Claude to "sync ideas from Keep" and it will diff Keep
  against `IDEAS.md` and merge new entries.
- The automation Chrome profile must be logged into Google once for
  this to work. If Claude gets a sign-in page, log in from the window
  it opens and tell it to retry.
- Fallback: Google Takeout export of Keep, or paste the list into chat.

Keep remains the capture tool (phone-friendly); this folder is the
canonical backlog the blog actually works from.
