"""Look things up in the two priručnici and report the PRINTED page number.

Rule 3 of the handoff: the PDF->printed offset is not constant, so a printed page
may never be assumed. This builds the folio map by reading the page number off the
top/bottom margin of each page, then uses it for every lookup.

    python booktool.py map                 # offset map, run ranges
    python booktool.py find RK decibel     # every printed page whose text matches
    python booktool.py page RK 53          # dump one printed page
    python booktool.py toc RK              # headings that look like section titles
"""
import re
import sys
from pathlib import Path

import pymupdf

DOCS = Path(r"g:/My Drive/Electronics/HAM Radio License/docs")
BOOKS = {
    # Radiokomunikacije.pdf is a pure scan with no text layer; the searchable copy is the
    # OCR'd one, and it is page-for-page identical, so citations derived here still apply.
    "RK": DOCS / "Radiokomunikacije_ocr.pdf",
    "PZM": DOCS / "Pasaric_Radioamaterizam_za_mlade.pdf",
    "ZBIRKA": DOCS / "ZBIRKA-1_Prirucnik-Radiokomunikacije-2023.pdf",
    "NN150/22": DOCS / "Pravilnik_o_amaterskim_radijskim_komunikacijama_NN_150_22.pdf",
    "ODLUKA": DOCS / "RA_ispiti_1_Odluka_o_provodjenju_ispita.pdf",
    "OBVEZNI": DOCS / "Obvezni_dio_ispitnog_programa.pdf",
    "TR61-01": DOCS / "CEPT_preporuka_TR61_01.pdf",
    "TR61-02": DOCS / "CEPT_Preporuka_TR61_02.pdf",
    "ERC32": DOCS / "ERCRep32.pdf",
}
MARGIN = 0.12  # fraction of page height treated as header/footer


def folio(page):
    """The printed page number as it appears in the page's own margin, or None.

    The OCR often glues the folio onto the end of the last body block instead of leaving
    it standing alone, so a block that merely ENDS in a bare number counts too — with the
    block's last line checked, not the whole block, to avoid catching a number mid-sentence.
    """
    h = page.rect.height
    best = None
    for x0, y0, x1, y1, txt, *_ in page.get_text("blocks"):
        s = txt.strip()
        top, bottom = y0 < h * MARGIN, y1 > h * (1 - MARGIN)
        if re.fullmatch(r"\d{1,3}", s) and (top or bottom):
            best = int(s) if bottom or best is None else best
        elif bottom and (last := s.splitlines()[-1].strip() if s else ""):
            if re.fullmatch(r"\d{1,3}", last):
                best = int(last)
    return best


def monotonic(read):
    """Drop folios that cannot be real, keeping the longest run that increases with the page.

    Reading a trailing number off the last block also picks up stray numerals — a figure
    caption, a table cell, a year in the colophon. A genuine folio always rises as you turn
    the page, so the longest strictly-increasing subsequence is the set of real ones and
    everything outside it is noise. (Longest-increasing-subsequence, O(n²); n is a few hundred.)
    """
    idx = sorted(read)
    if not idx:
        return {}
    best = [1] * len(idx)
    prev = [-1] * len(idx)
    for a in range(len(idx)):
        for b in range(a):
            if read[idx[b]] < read[idx[a]] and best[b] + 1 > best[a]:
                best[a], prev[a] = best[b] + 1, b
    a = max(range(len(idx)), key=lambda k: best[k])
    keep = []
    while a != -1:
        keep.append(idx[a])
        a = prev[a]
    return {i: read[i] for i in reversed(keep)}


def load(book):
    """Open a book and map pdf index <-> printed page.

    Plenty of pages carry no readable folio — a full-page figure, a chapter opener, or just
    OCR that dropped it. Those gaps are FILLED from the offset of the nearest page that does
    carry one, so a citation to such a page verifies instead of being reported as fictional.
    Only genuinely readable folios seed the map; the fill is interpolation, never invention.
    """
    doc = pymupdf.open(BOOKS[book])
    read = {}                                   # pdf index -> folio actually read
    for i, page in enumerate(doc):
        f = folio(page)
        if f is not None:
            read[i] = f
    read = monotonic(read)

    pdf2pr = dict(read)
    anchors = sorted(read)
    for i in range(doc.page_count):
        if i in pdf2pr or not anchors:
            continue
        near = min(anchors, key=lambda a: abs(a - i))
        # only extend an offset across a short gap; a long unnumbered stretch may hide a
        # section of inserted plates, and guessing across it would be invention
        if abs(near - i) <= 4:
            pdf2pr[i] = read[near] + (i - near)

    printed = {}
    for i in sorted(pdf2pr):
        printed.setdefault(pdf2pr[i], i)
    return doc, printed, pdf2pr


def cmd_map(book):
    doc, printed, pdf2pr = load(book)
    print(f"{book}: {doc.page_count} pdf pages, {len(pdf2pr)} carry a printed folio")
    runs, prev = [], None
    for i in sorted(pdf2pr):
        off = pdf2pr[i] - i
        if prev is None or off != prev[2]:
            runs.append([i, i, off])
        else:
            runs[-1][1] = i
        prev = runs[-1]
    print("  pdf index range -> printed = index + offset")
    for a, b, off in runs:
        if b - a >= 1:
            print(f"    pdf {a:4d}..{b:4d}   offset {off:+d}   (printed {a+off}..{b+off})")
    print("  unnumbered pdf pages:",
          [i for i in range(doc.page_count) if i not in pdf2pr][:40])


def cmd_find(book, *terms):
    doc, printed, pdf2pr = load(book)
    pat = re.compile("|".join(re.escape(t) for t in terms), re.I)
    for i, page in enumerate(doc):
        txt = page.get_text()
        hits = pat.findall(txt)
        if not hits:
            continue
        pr = pdf2pr.get(i)
        head = next((l.strip() for l in txt.splitlines() if l.strip()), "")
        print(f"pdf {i:4d}  printed {pr if pr is not None else '?':>4}  "
              f"x{len(hits):<3} {head[:70]}")


def cmd_page(book, printed_no):
    """`page RK 205` prints printed page 205; `page RK pdf201` prints pdf index 201."""
    doc, printed, pdf2pr = load(book)
    if str(printed_no).startswith("pdf"):
        i = int(str(printed_no)[3:])
        print(f"### {book} pdf index {i} = printed {pdf2pr.get(i, '?')}\n")
    else:
        i = printed.get(int(printed_no))
        if i is None:
            sys.exit(f"no page resolves to printed {printed_no}; run `map` to see what exists")
        print(f"### {book} printed {printed_no} = pdf index {i}\n")
    print(doc[i].get_text())


def cmd_toc(book):
    doc, printed, pdf2pr = load(book)
    for i, page in enumerate(doc):
        for line in page.get_text().splitlines():
            s = line.strip()
            if re.match(r"^\d+(\.\d+)*\.?\s+\S", s) and len(s) < 70 and not s.endswith(","):
                print(f"printed {pdf2pr.get(i, '?'):>4}  {s}")


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:] or ["map"]
    {"map": cmd_map, "find": cmd_find, "page": cmd_page, "toc": cmd_toc}[cmd](*rest)
