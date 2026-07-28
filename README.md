# wossname? — aweussom.github.io

Tech blog, built with [Pelican](https://getpelican.com/). Markdown in, site out.

## Publishing a post

1. Add `content/YYYY-MM-DD-some-slug.md`:

   ```markdown
   Title: The post title
   Date: 2026-07-28 12:00
   Slug: some-slug
   Tags: linux, llm
   Summary: One-line teaser for the front page and feeds.

   Body in Markdown.
   ```

2. Push to `main`. GitHub Actions builds and deploys to
   https://aweussom.github.io/ — nothing generated is ever committed.

## Cross-posting to dev.to

The blog is canonical; dev.to is the mirror. dev.to → Settings →
Extensions → "Publishing to DEV Community from RSS" pointed at
`https://aweussom.github.io/feeds/all.atom.xml` creates drafts
automatically with `canonical_url` set here. Publish the draft on
dev.to when ready.

## Importing from dev.to (historical)

`python scripts/import_devto.py` re-fetches all dev.to posts, backdates
them, and localizes images. Used for the initial 2026 import; safe to
re-run (overwrites imported files).

## Local preview

```bash
pip install "pelican[markdown]"
pelican content -s pelicanconf.py -o output
pelican --listen   # or open output/index.html
```
