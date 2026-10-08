"""kona_page.py - build the Kona & Co page from the comic repo's publishing log.

    python scripts/kona_page.py            # writes content/pages/kona.md + images
    python scripts/kona_page.py --check    # list what would change, exit 1 if anything

Reads prosjekter/kona/publisert/facebook-profile/ in the comic repo: one dated
symlink per strip that has actually been posted. Only those strips appear
here, newest first, so the blog never shows the unpublished buffer. Titles
come from the drafts' frontmatter. Strips are converted to JPEG at 1072 px
wide into content/images/kona/. Pages are outside the Atom feed, so dev.to
does not see them. Run it, read the diff, push.
"""
import argparse
import re
import sys
from pathlib import Path

BLOG = Path(__file__).resolve().parent.parent
COMIC = Path(r"C:\devel\aweussom\python\konaogco\prosjekter\kona")
LOG = COMIC / "publisert" / "facebook-profile"
PAGE = BLOG / "content" / "pages" / "kona.md"
IMG = BLOG / "content" / "images" / "kona"

INTRO = """Kona & Co is my daily comic: me, Kona, and the dogs Missy and Saga. Dry
Norwegian everyday humour, four vertical panels, cross-stitch embroideries
with rude text on the wall. In Norwegian, because that is the language it
happens in. One strip a day on Facebook; this page collects the ones that
have gone out, newest first. Drawn with image models from a short draft and
a set of character cards; the tooling is described in the blog posts.
"""


def title_of(stem: str) -> str:
    """'007-hundeminutter' -> the draft's tittel, else the slug prettified."""
    for p in (COMIC / "utkast").glob(f"{stem}*.md"):
        m = re.search(r"^tittel:\s*(.+)$", p.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip()
    return stem.split("-", 1)[-1].replace("-", " ").capitalize()


def published() -> list[tuple[str, str, Path]]:
    """[(date, stem, strip path)] newest first, from the dated links."""
    out = []
    for p in LOG.iterdir():
        m = re.match(r"(\d{4}-\d{2}-\d{2})_(.+)\.(png|jpg)$", p.name)
        if not m:
            continue
        target = p.resolve() if p.is_symlink() else COMIC / "striper" / f"{m.group(2)}.{m.group(3)}"
        if not target.exists():
            target = COMIC / "striper" / f"{m.group(2)}.{m.group(3)}"
        out.append((m.group(1), m.group(2), target))
    return sorted(out, reverse=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--width", type=int, default=1072)
    args = ap.parse_args()
    from PIL import Image

    strips = published()
    if not strips:
        sys.exit(f"ingen publiserte striper i {LOG}")
    IMG.mkdir(parents=True, exist_ok=True)
    changed = []
    lines = ["Title: Kona & Co", "Slug: kona", "Summary: A daily Norwegian comic about Kona, me and the dogs; the strips that have been published so far.", "", INTRO, ""]
    for date, stem, src in strips:
        jpg = IMG / f"{stem}.jpg"
        if not jpg.exists() or jpg.stat().st_mtime < src.stat().st_mtime:
            changed.append(jpg.name)
            if not args.check:
                im = Image.open(src).convert("RGB")
                if im.width != args.width:
                    im = im.resize((args.width, round(im.height * args.width / im.width)), Image.LANCZOS)
                im.save(jpg, quality=85, optimize=True)
        title = title_of(stem)
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"<time>{date}</time>")
        lines.append("")
        lines.append(f"![{title}]({{static}}/images/kona/{stem}.jpg)")
        lines.append("")
    text = "\n".join(lines).rstrip() + "\n"
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != text:
        changed.append(PAGE.name)
        if not args.check:
            PAGE.parent.mkdir(parents=True, exist_ok=True)
            PAGE.write_text(text, encoding="utf-8")
    if changed:
        print(("would change: " if args.check else "wrote: ") + ", ".join(changed))
        if args.check:
            sys.exit(1)
    else:
        print("kona.md er ajour")
    print(f"{len(strips)} striper publisert, nyeste {strips[0][0]} {strips[0][1]}")


if __name__ == "__main__":
    main()
