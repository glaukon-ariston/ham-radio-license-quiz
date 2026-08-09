"""Create the next queue item.

    python queue/new.py P1 "figures2 misses stacked options"

Numbers are allocated across todo/ AND done/ so they are never reused — an item
number stays a stable reference after the work has landed.
"""
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
TODO, DONE = HERE / "todo", HERE / "done"
BANDS = ("P1", "P2", "P3")


def slug(title):
    # Croatian diacritics fold to ASCII so filenames stay portable.
    flat = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", flat.lower())).strip("-")[:48]


def main(argv):
    if len(argv) < 3 or argv[1].upper() not in BANDS:
        sys.exit(f"usage: python queue/new.py {'|'.join(BANDS)} \"title\"")
    prio, title = argv[1].upper(), " ".join(argv[2:]).strip()
    if not title:
        sys.exit("a title is required")

    TODO.mkdir(parents=True, exist_ok=True)
    DONE.mkdir(parents=True, exist_ok=True)
    used = [int(m.group(1)) for p in list(TODO.glob("P?-*.md")) + list(DONE.glob("P?-*.md"))
            if (m := re.match(r"P\d-(\d+)-", p.name))]
    n = max(used, default=0) + 1

    body = (HERE / "TEMPLATE.md").read_text(encoding="utf-8")
    body = body.replace(
        '# <one-line title, imperative: "Fix ...", "Add ...", "Classify ...">', f"# {title}")
    body = re.sub(r"^prio:( +)P2$", rf"prio:\g<1>{prio}", body, count=1, flags=re.M)

    path = TODO / f"{prio}-{n:04d}-{slug(title)}.md"
    if path.exists():
        sys.exit(f"refusing to overwrite {path}")
    path.write_text(body, encoding="utf-8")
    print(path.relative_to(HERE.parent).as_posix())


if __name__ == "__main__":
    main(sys.argv)
