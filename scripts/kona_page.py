"""kona_page.py - build the Kona & Co pages from the comic repo's publishing log.

    python scripts/kona_page.py            # writes content/pages/kona*.md + images
    python scripts/kona_page.py --check    # list what would change, exit 1 if anything

Reads prosjekter/kona/publisert/facebook-profile/ in the comic repo: one dated
symlink per strip that has actually been posted. Only those strips appear
here, newest first, so the blog never shows the unpublished buffer. Titles
come from the drafts' frontmatter.

Two kinds of page, both Pelican *pages* (outside the Atom feed, so dev.to
never mirrors them):

- kona.md, the index: one card per strip, newest first.
- kona-<stem>.md, the viewer for one strip: the portrait panels from
  prosjekter/kona/paneler/<stem>/ stacked, each scaled to fit the screen
  height on a desktop and the width on a phone. Strips without portrait
  panels get the strip image itself.

Images go under content/images/kona/<stem>/.
"""
import argparse
import re
import sys
from pathlib import Path

BLOG = Path(__file__).resolve().parent.parent
COMIC = Path(r"C:\devel\aweussom\python\konaogco\prosjekter\kona")
LOGS = [COMIC / "publisert" / "facebook-profile", COMIC / "publisert" / "blogg"]
PAGES = BLOG / "content" / "pages"
IMG = BLOG / "content" / "images" / "kona"

INTRO = """Kona & Co is my daily comic: me, Kona, and the dogs Missy and Saga. Dry
Norwegian everyday humour, cross-stitch embroideries with rude text on the
wall. In Norwegian, because that is the language it happens in. One strip a
day on Facebook; this page collects the ones that have gone out, newest
first. Click one to read it panel by panel. Drawn with image models from a
short draft and a set of character cards; the tooling is described in the
blog posts.
"""


def title_of(stem: str) -> str:
    for p in (COMIC / "utkast").glob(f"{stem}*.md"):
        m = re.search(r"^tittel:\s*(.+)$", p.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip()
    return stem.split("-", 1)[-1].replace("-", " ").capitalize()


def published() -> list[tuple[str, str, Path]]:
    """Strips that have gone out on any logged channel; the blog itself is a
    channel (publisert/blogg/), so a strip can appear here before Facebook.
    One entry per strip, dated by its first appearance."""
    first: dict[str, tuple[str, Path]] = {}
    for log in LOGS:
        if not log.exists():
            continue
        for p in log.iterdir():
            m = re.match(r"(\d{4}-\d{2}-\d{2})_(.+)\.(png|jpg)$", p.name)
            if not m:
                continue
            date, stem, ext = m.groups()
            if stem not in first or date < first[stem][0]:
                first[stem] = (date, COMIC / "striper" / f"{stem}.{ext}")
    return sorted(((d, stem, t) for stem, (d, t) in first.items()), reverse=True)


class Build:
    def __init__(self, check: bool, width: int):
        self.check, self.width, self.changed = check, width, []

    def image(self, src: Path, dst: Path, width: int | None = None) -> None:
        from PIL import Image

        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            return
        self.changed.append(dst.relative_to(BLOG).as_posix())
        if self.check:
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(src).convert("RGB")
        w = width or self.width
        if im.width != w:
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(dst, quality=85, optimize=True)

    def text(self, dst: Path, body: str) -> None:
        if dst.exists() and dst.read_text(encoding="utf-8") == body:
            return
        self.changed.append(dst.relative_to(BLOG).as_posix())
        if not self.check:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(body, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--width", type=int, default=1080)
    args = ap.parse_args()
    b = Build(args.check, args.width)
    strips = published()
    if not strips:
        sys.exit("ingen publiserte striper i loggen")

    index = ["Title: Kona & Co", "Slug: kona",
             "Summary: A daily Norwegian comic about Kona, me and the dogs; the strips that have been published so far.",
             "", INTRO, "", '<div class="kona-grid">']
    for date, stem, strip in strips:
        title = title_of(stem)
        panels = sorted((COMIC / "paneler" / stem).glob("*.jpg"), key=lambda p: int(p.stem)) if (COMIC / "paneler" / stem).exists() else []
        b.image(strip, IMG / stem / "strip.jpg")
        for p in panels:
            b.image(p, IMG / stem / f"panel-{p.stem}.jpg")
        thumb = f"panel-{panels[0].stem}.jpg" if panels else "strip.jpg"
        index.append(f'<a class="kona-card" href="{{filename}}kona-{stem}.md"><img src="{{static}}/images/kona/{stem}/{thumb}" alt="{title}" loading="lazy"><span>{title}</span><time>{date}</time></a>')
        # the viewer page
        view = [f"Title: {title}", f"Slug: kona-{stem}", f"Summary: Kona & Co, {date}: {title}.", ""]
        view.append(f'<p class="kona-back"><a href="{{filename}}kona.md">Kona &amp; Co</a> · <time>{date}</time></p>')
        view.append("")
        if panels:
            view.append('<div class="kona-reader">')
            for p in panels:
                view.append(f'<img src="{{static}}/images/kona/{stem}/panel-{p.stem}.jpg" alt="{title}, panel {p.stem}">')
            view.append("</div>")
            view.append("")
            view.append(f'<p class="kona-strip-link"><a href="{{static}}/images/kona/{stem}/strip.jpg">The strip as one image</a></p>')
        else:
            view.append('<div class="kona-reader kona-reader-strip">')
            view.append(f'<img src="{{static}}/images/kona/{stem}/strip.jpg" alt="{title}">')
            view.append("</div>")
        b.text(PAGES / f"kona-{stem}.md", "\n".join(view).rstrip() + "\n")
    index.append("</div>")
    b.text(PAGES / "kona.md", "\n".join(index).rstrip() + "\n")

    if b.changed:
        print(("would change: " if args.check else "wrote: ") + ", ".join(b.changed))
        if args.check:
            sys.exit(1)
    else:
        print("kona-sidene er ajour")
    print(f"{len(strips)} striper publisert, nyeste {strips[0][0]} {strips[0][1]}")


if __name__ == "__main__":
    main()
