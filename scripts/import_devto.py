#!/usr/bin/env python3
"""Import dev.to articles as Pelican content.

Fetches all published articles for DEVTO_USERNAME, writes each as
content/YYYY-MM-DD-slug.md with Pelican frontmatter (backdated to the
original publish time), downloads any dev.to-hosted images into
content/images/<slug>/ and rewrites the links to {static} paths.

Re-runnable: existing files are overwritten, so edits belong on dev.to
or in this repo after you stop mirroring a post (then drop it from the
import by adding its id to SKIP_IDS).
"""

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

DEVTO_USERNAME = "tommy_leonhardsen_81d1f4e"
SKIP_IDS: set[int] = set()

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
UA = {"User-Agent": "wossname-blog-import/1.0"}

IMG_RE = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)\)")
LIQUID_RE = re.compile(r"\{%-?\s*\w+\s+(\S+?)\s*-?%\}")
FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)


def get_json(url: str):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r:
        return json.load(r)


def download(url: str, dest: Path) -> bool:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:  # keep the remote URL on failure
        print(f"    ! image failed ({e}): {url}", file=sys.stderr)
        return False


def clean_slug(slug: str) -> str:
    return re.sub(r"-[a-z0-9]{4}$", "", slug)


def ext_of(url: str) -> str:
    m = re.search(r"\.(png|jpe?g|gif|webp|svg)(?:$|\?)", url, re.I)
    return m.group(1).lower() if m else "png"


def import_article(article_id: int) -> None:
    a = get_json(f"https://dev.to/api/articles/{article_id}")
    slug = clean_slug(a["slug"])
    body = a.get("body_markdown") or ""
    body = FRONTMATTER_RE.sub("", body)
    body = LIQUID_RE.sub(r"<\1>", body)

    imgdir = CONTENT / "images" / slug
    counter = 0

    def localize(m: re.Match) -> str:
        nonlocal counter
        alt, url = m.group(1), m.group(2)
        if "dev.to" not in url and "dev-to-uploads" not in url:
            return m.group(0)
        counter += 1
        name = f"{counter:02d}.{ext_of(url)}"
        imgdir.mkdir(parents=True, exist_ok=True)
        if download(url, imgdir / name):
            return f"![{alt}]({{static}}/images/{slug}/{name})"
        return m.group(0)

    body = IMG_RE.sub(localize, body)

    date = a["published_at"][:16].replace("T", " ")
    tags = ", ".join(a.get("tags") or [])
    summary = (a.get("description") or "").replace("\n", " ").strip()
    lines = [
        f"Title: {a['title']}",
        f"Date: {date}",
        f"Slug: {slug}",
    ]
    if tags:
        lines.append(f"Tags: {tags}")
    if summary:
        lines.append(f"Summary: {summary}")
    lines.append(f"Original: {a['url']}")
    out = CONTENT / f"{a['published_at'][:10]}-{slug}.md"
    out.write_text("\n".join(lines) + "\n\n" + body.strip() + "\n", encoding="utf-8")
    print(f"  wrote {out.relative_to(ROOT)} ({counter} images)")


def main() -> None:
    CONTENT.mkdir(exist_ok=True)
    articles = get_json(
        f"https://dev.to/api/articles?username={DEVTO_USERNAME}&per_page=100"
    )
    print(f"{len(articles)} articles on dev.to")
    for a in articles:
        if a["id"] in SKIP_IDS:
            continue
        print(f"- {a['published_at'][:10]} {a['title']}")
        import_article(a["id"])
        time.sleep(0.5)


if __name__ == "__main__":
    main()
