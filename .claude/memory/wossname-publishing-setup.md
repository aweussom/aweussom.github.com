---
name: wossname-publishing-setup
description: "The author/blog publishing architecture decided July 2026 — org, repos, and what remains to build"
metadata: 
  node_type: memory
  type: project
  originSessionId: bc73b6cc-4d85-456d-8ed7-87b1b572874d
  modified: 2026-07-28T20:46:52.325Z
---

Decided 2026-07-28: Tommy's publishing setup is **two identities, one toolchain**.

- **Tech blog**: `aweussom/aweussom.github.com` (serves aweussom.github.io). **DONE 2026-07-28**: single `main` branch (now default), Pelican 4.12, custom `theme/wossname` (matches books-site design), GitHub Actions deploy (Pages build_type=workflow). All 9 dev.to posts imported+backdated via `scripts/import_devto.py` (re-runnable); old 2020 posts retired (history on `master`/`source` branches). dev.to username: `tommy_leonhardsen_81d1f4e`. dev.to RSS import is ENABLED (he did it 2026-07-28) — future posts auto-draft on dev.to with canonical_url home; existing 9 dev.to posts still need canonical_url set manually/via API key. Blog repo has `CLAUDE.md` (auto-loaded pointer), `README.md` (full playbook) and `VOICE.md` (his writing style guide — follow it for any post content).
- **Author org**: `wossname-books` (user picked the name; he is admin). Landing page repo `wossname-books/wossname-books.github.io` is LIVE — single static index.html, ambigram flip wordmark (wossname ⟲ aweussom), 4 book cards. Edit + push = deploy.
- **Book repos** (all under `C:\devel\aweussom\bok\`, on aweussom account):
  - `edenrise` + `coldpay` — PUBLISHED novels on Amazon KDP (B0G4HWJMLL, B0GM94Y5ZJ), **both in KDP Select/Kindle Unlimited** → max 10% of each book may be free elsewhere. Chapter-one excerpt pages are LIVE on the landing site (Edenrise trimmed to 8.95%, Coldpay full ch1 = 3.9%); keep any future excerpt additions under the cap.
  - `oldgods` — **The Weave Beneath The World**, NEXT to be published (19 ch, ~73k words, final rewrite; KDP store copy + epub ready). Featured as "Next up" on the landing page.
  - `OldManYellsAt` — English tech book, 15 chapters drafted; plan: serialize to blog + dev.to.
  - `humor-og-han-baeffar` — Norwegian memoir novel; raw stories in its `blog/` dirs; publish opt-in via sync (book repo stays canonical).
  - AUTHOR.md blurbs committed in OldManYellsAt and humor-og-han-baeffar (local commits, NOT pushed — his call).

**Why:** audiences differ (EN tech vs NO literary), but he *wants* the personas connected.
**How to apply:** new posts/excerpts are Markdown in git; publishing is always a git push, never a platform API. See [[wossname-identity]].
