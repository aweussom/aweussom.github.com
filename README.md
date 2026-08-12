# wossname? — publishing HQ

Tech blog source for **https://aweussom.github.io/**, and the operating
manual for the rest of the Wossname publishing estate. Written for both
humans and future Claude sessions: everything below is doable with
`git`, `gh` (authenticated as `aweussom`), and Python.

## The estate map

| What | Where (local) | Where (live) |
|---|---|---|
| Tech blog (this repo) | `C:\devel\aweussom\blog\aweussom.github.com` | https://aweussom.github.io/ |
| Author landing page | `C:\devel\aweussom\wossname-books.github.io` | https://wossname-books.github.io/ |
| Book repos | `C:\devel\aweussom\bok\{edenrise,coldpay,oldgods,OldManYellsAt,humor-og-han-baeffar,...}` | Amazon / unpublished |

GitHub: blog + book repos live on the `aweussom` account; the landing
page lives in the `wossname-books` org (aweussom is owner).

## Publish a blog post (the main event)

1. Create `content/YYYY-MM-DD-some-slug.md`:

   ```markdown
   Title: The post title
   Date: 2026-07-28 12:00
   Slug: some-slug
   Tags: linux, llm
   Summary: One-line teaser for the front page and feeds.

   Body in Markdown. Images go in content/images/<slug>/ and are
   referenced as ![alt]({static}/images/<slug>/file.png).
   ```

2. Commit and push to `main`. GitHub Actions (`.github/workflows/deploy.yml`)
   builds with Pelican and deploys to Pages. Never commit generated HTML.
3. Verify: `gh run list --limit 1` goes green, then check
   https://aweussom.github.io/ (the post should be on top unless backdated).

Backdating works — `Date:` is trusted as written. Ordering, archives,
and feeds all follow it.

### Drafts and ideas (local only)

`ideas/` (post backlog) and `blog_drafts/` (posts in progress) are
gitignored on purpose: this repo is public, so anything committed here
is world-readable before it's published. Both live only on this
machine — don't force-add them. A draft graduates by moving into
`content/` with proper metadata.

### Local preview (optional)

```bash
pip install "pelican[markdown]"
pelican content -s pelicanconf.py -o output   # then open output/index.html
```

## Cross-posting to dev.to

Rule: **the blog is canonical, dev.to is the mirror.** dev.to profile:
`tommy_leonhardsen_81d1f4e`.

- Ongoing: dev.to → Settings → Extensions → "Publishing from RSS"
  pointed at `https://aweussom.github.io/feeds/all.atom.xml` creates
  drafts with `canonical_url` set here. Tommy publishes the draft.
- Historical import (already done for the 9 posts up to June 2026):
  `python scripts/import_devto.py` re-fetches everything from dev.to,
  backdates, and localizes images. Safe to re-run; it overwrites.

## Landing page (wossname-books.github.io)

One hand-written `index.html`, no build step: edit, commit, push to
`main`, Pages redeploys in under a minute. House style lives in that
file — Literata + IBM Plex Mono, light "polar day" / dark "mørketid"
palettes, one accent color per book (Edenrise violet, Coldpay oxblood,
Weave aurora, OMYAC amber, Humor fjord). The hero wordmark is the
wossname⟲aweussom ambigram flip — keep it.

Book cards follow a fixed pattern (`article.book.<bookclass>` with
genre eyebrow / title / pitch / status line). New book = new accent
variable + card. Sections: In print → Next up → On the bench.

## Book excerpts — READ THIS BEFORE ADDING ANY

Edenrise and Coldpay are enrolled in **KDP Select**, which allows at
most **10% of a book** to be freely available elsewhere. Current state
(checked July 2026):

- `edenrise-chapter-one.html` — chapter 1 trimmed to 8.95%
- `coldpay-chapter-one.html` — full chapter 1, 3.9%

Do not extend these or add excerpts beyond 10% of any Select-enrolled
book. Manuscripts live in the book repos (`*-kdp.md` is the full text —
never commit or publish it anywhere public).

## Book repos

- Each has `AUTHOR.md` (canonical bio blurbs — reuse, don't rewrite).
- `oldgods` = *The Weave Beneath The World*, next up for publication.
- `humor-og-han-baeffar` (Norwegian memoir): its `blog/` folders are
  raw source stories; the plan is opt-in syncing to a future site, book
  repo stays canonical.
- Book repos may hold local commits that are deliberately unpushed —
  ask before pushing anything in `C:\devel\aweussom\bok\`.

## Voice notes

English blurbs and copy: dry, wry, concrete (see `AUTHOR.md` in
OldManYellsAt). Norwegian: warm bokmål (see humor-og-han-baeffar).
The nickname gag — "if you've forgotten it, you remember it", in use
since 1991 — is load-bearing brand; treat it kindly.
