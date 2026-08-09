"""Crop the figures that HRS technical questions depend on.

The exam PDFs come out of PrimoPDF, which draws every line as a one-pixel-high INLINE
image -- 949 of them on page 3 alone. `page.get_images()` does not report inline images
and `page.get_drawings()` does not see them either, so both APIs answer "this page has
no graphics" for a page that plainly shows a circuit. Clustering drawing paths is
therefore impossible; the only thing that knows a figure is there is the rendered
pixels. So we crop the vertical band a question owns -- from below its last option line
down to the next question's stem -- and decide by measuring ink, never by asking the PDF
what it contains.
"""
import json, re
from pathlib import Path
import pymupdf
import parse2

PDF = parse2.DOCS / "RA_ispiti_9_A_razred_Tehnicki_dio.pdf"
OUT = Path(__file__).parent
FIGS = OUT / "figs"
FIGS.mkdir(exist_ok=True)
DPI = 190
Q_RE = re.compile(r"^(\d{1,3})\.\s*(.*)$")

def postprocess(path: Path):
    """Neutralise the red answer-marking inside a crop, then trim whitespace.

    27 of the 45 figures contain the red mark that identifies the correct option.
    Left as-is, the picture gives the answer away before you have chosen. This MUST
    stay part of the cropping step -- when it lived in a separate ad-hoc script, a
    later rebuild silently restored the red marks.
    """
    from PIL import Image, ImageChops
    import numpy as np

    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 100) & (r - g > 50) & (r - b > 50)
    if red.any():
        a[red] = [0, 0, 0]
        im = Image.fromarray(a.astype("uint8"))

    bg = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 18 else 0).getbbox()
    if box:
        pad = 8
        box = (max(box[0] - pad, 0), max(box[1] - pad, 0),
               min(box[2] + pad, im.width), min(box[3] + pad, im.height))
        if (box[2] - box[0]) > 30 and (box[3] - box[1]) > 25:
            im = im.crop(box)
    im.save(path, optimize=True)
    return im.width, im.height, path.stat().st_size


def ink_pixels(path: Path) -> int:
    """Non-white pixels in a crop — how much drawing it actually contains."""
    from PIL import Image
    import numpy as np
    return int((np.array(Image.open(path).convert("L")) < 200).sum())


DETECT_DPI = 100
DETECT_INK = 300


def nontext_ink(page, box) -> int:
    """Dark pixels inside `box` that no character accounts for — i.e. drawing.

    Render the band, paint every glyph white, count what survives. Text is masked at
    CHARACTER level and not by line or span: the figure labels sit on baselines whose
    spans are padded with dozens of leading spaces, so a span-level mask covers the
    drawing itself and reports a spectrum as blank paper (q112 did exactly that).
    Spaces are not masked — they have a bbox but leave no ink.
    """
    import numpy as np
    pix = page.get_pixmap(clip=box, dpi=DETECT_DPI)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    g = a[..., :3].min(axis=2).astype(int)
    s = DETECT_DPI / 72.0
    for blk in page.get_text("rawdict", clip=box)["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                for ch in sp["chars"]:
                    if not ch["c"].strip():
                        continue
                    x0, y0, x1, y1 = ch["bbox"]
                    r0, r1 = max(int((y0 - box.y0) * s) - 2, 0), int((y1 - box.y0) * s) + 3
                    c0, c1 = max(int((x0 - box.x0) * s) - 2, 0), int((x1 - box.x0) * s) + 3
                    g[r0:r1, c0:c1] = 255
    return int((g < 200).sum())


bank = {q["id"]: q for q in json.load(open(OUT / "bank.json", encoding="utf-8"))}
doc = pymupdf.open(PDF)

# Questions the source never numbered. They are real questions with their own figure, but
# because no "186." anchors them they never became a boundary: the preceding question's
# extent swallowed their stem AND their options, so its crop band slid down past its own
# figure and landed on theirs. That is how q186 came to show the quad belonging to 186b.
# Anchor them by their stem text instead.
UNNUMBERED = {q["id"]: q for q in bank.values() if int(q["number"]) != q["number"]}

# A stem that needs its figure but names no "slika" — the picture IS the question.
FORCE_FIGURE = {"teh-186b"}


def stem_anchor(page, q):
    """y of the unnumbered question's stem on this page, or None."""
    head = " ".join(q["question"].split())[:25].lower()
    for x0, text, red, ym in parse2.cells(page):
        if " ".join(text.split()).lower().startswith(head):
            return ym
    return None


def page_floor(page):
    """y above the folio number, so the last question on a page does not crop it in.

    Every page ends with a bare page number at the outer margin. The band of the last
    question runs to the bottom of the paper, so that digit came along inside the crop
    and survived the whitespace trim (it is ink like any other).
    """
    H = page.rect.height
    ys = [ym for x0, text, red, ym in parse2.cells(page)
          if ym > H - 70 and text.strip().isdigit()]
    return min(ys) - 10 if ys else H - 40


# y-extent of every question on every page
layout: dict[int, list] = {}
for pno, page in enumerate(doc):
    entries, opt_ys = [], []
    for x0, text, red, ym in parse2.cells(page):
        t = text.strip()
        if parse2.OPT_RE.match(t):
            opt_ys.append(ym)
        m = Q_RE.match(t)
        if m and not parse2.OPT_RE.match(t):
            entries.append({"num": int(m.group(1)), "start": ym, "last": ym, "opt": ym})
        elif entries:
            entries[-1]["last"] = max(entries[-1]["last"], ym)
            # A figure's own labels ("25 Ω", "= 5 V") are text cells too, so "last text
            # line" runs PAST the drawing and the crop band lands on blank paper below it
            # -- that is how q43 became a 181x41 sliver. Track the last OPTION line
            # separately and start the band there, so labelled figures stay inside it.
            if parse2.OPT_RE.match(t):
                entries[-1]["opt"] = max(entries[-1]["opt"], ym)

    for qid, q in UNNUMBERED.items():
        if q.get("page") != pno + 1:
            continue
        y = stem_anchor(page, q)
        if y is None:
            continue
        # the stem ends the previous question, and starts one of its own
        for e in entries:
            if e["start"] < y:
                e["last"] = min(e["last"], y - 14)   # clear of the next stem's ascenders
        # ...and so do its options. The e)-h) below an unnumbered stem had pushed q186's
        # "last option line" past its own figure, so its band began below the drawing,
        # came back blank, and fell through to the whole-question band — which then showed
        # the four options, the marked one still recognisable by its different typeface.
        prev = max((e for e in entries if e["start"] < y), key=lambda e: e["start"],
                   default=None)
        if prev is not None:
            own = [ym for ym in opt_ys if prev["start"] < ym < y]
            if own:
                prev["opt"] = max(own)
        entries.append({"num": q["number"], "id": qid, "start": y, "last": y})
        entries.sort(key=lambda e: e["start"])
        # options below an unnumbered stem belong to it, not to the question above
        nxt = next((e["start"] for e in entries if e["start"] > y), None)
        for x0, text, red, ym in parse2.cells(page):
            if y < ym and (nxt is None or ym < nxt):
                entries[[e["start"] for e in entries].index(y)]["last"] = max(
                    entries[[e["start"] for e in entries].index(y)]["last"], ym)

    layout[pno] = entries

made = {}
found_by_ink = []
for pno, entries in layout.items():
    page = doc[pno]
    W, H = page.rect.width, page.rect.height
    floor = page_floor(page)
    for i, e in enumerate(entries):
        qid = e.get("id") or f"teh-{e['num']:03d}"
        q = bank.get(qid)
        if not q:
            continue
        nxt = entries[i + 1]["start"] - 6 if i + 1 < len(entries) else floor
        # The stem is only a hint. Six questions show a drawing and never mention it —
        # "Izračunaj vrijednost struje I3!" is a bare imperative with a node diagram under
        # it — so a question also earns a figure by having ink below its options that no
        # character accounts for. Measured on the band BELOW the options, not on the whole
        # question: q17 and q81 carry their formula as an image inside the STEM, already
        # transcribed by overrides.json, and must not be re-shown as a picture of
        # themselves. The measured gap is wide (0 for every text-only question, ≥1000 for
        # all six real ones), so the threshold is not delicate.
        needs = bool(re.search(r"\b(slika|slici|sliku|shem|crtež|crtez|dijagram|oscilogram|skic)",
                               q["question"], re.I)) or q.get("figure_options") \
            or qid in FORCE_FIGURE
        if not needs:
            band = pymupdf.Rect(70, max(e.get("opt", e["last"]) + 6, 30), W - 45,
                                min(nxt, H - 30))
            if band.height < 25 or nontext_ink(page, band) < DETECT_INK:
                continue
            found_by_ink.append(qid)

        # Two layouts occur and nothing in the text tells them apart: the figure sits BELOW
        # the options (usual), or BETWEEN the stem and the options (q74's filter curves).
        # Guessing from the geometry gets one of them wrong every time, so crop the likely
        # band first and fall back to the whole question block when it comes back empty --
        # a band that is nearly all white paper trims down to a sliver, which is the tell.
        # `last` is the last TEXT cell of the question, and on a bottom-of-page question
        # that cell is the folio number — so the wide band must be clamped to the floor
        # as well, or q74 ships with a stray "11" in the corner.
        candidates = [(e.get("opt", e["last"]) + 6, nxt),                    # below options
                      (e["start"] - 4, min(max(e["last"], nxt) + 4, floor))]  # whole question
        # Which band holds the drawing is decided by measuring, not by guessing from the
        # geometry: render both and keep whichever carries the DRAWING.
        name = f"{qid}.png"
        shot = []
        for n, (top, bottom) in enumerate(candidates):
            box = pymupdf.Rect(70, max(top, 30), W - 45, min(bottom, H - 30))
            if box.height < 25 or box.width < 40:
                continue
            pix = page.get_pixmap(clip=box, dpi=DPI)
            if pix.width < 30 or pix.height < 25:
                continue
            tmp = FIGS / f".{qid}.{n}.png"
            pix.save(tmp)
            w, h, _ = postprocess(tmp)
            if w < 120 or h < 60:
                tmp.unlink(missing_ok=True)
                continue
            shot.append((tmp, w, h, nontext_ink(page, box)))
        if shot:
            # The candidates are ordered tightest-first, and the tight one is what we want:
            # the whole-question band always carries more TOTAL ink simply because it
            # includes the stem and options, so the share is measured on drawing ink only.
            # Judging by total ink made q277 — four wordy options under a modest antenna
            # sketch — fail the share test and ship a picture of its own question, red
            # answer mark and all. Take the tightest band holding essentially the whole
            # drawing; fall through to the wider one only when the figure really does sit
            # between the stem and the options (q74's filter curves).
            most = max(s[3] for s in shot)
            tmp, w, h, _ = next((s for s in shot if s[3] >= 0.6 * most), shot[0])
            for s in shot:
                if s[0] != tmp:
                    s[0].unlink(missing_ok=True)
            tmp.replace(FIGS / name)
            made[qid] = {"file": name, "page": pno + 1, "w": w, "h": h,
                         "bytes": (FIGS / name).stat().st_size}

json.dump(made, open(OUT / "figs_index.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

want = [q["id"] for q in bank.values()
        if q["section"] == "tehnicki"
        and (re.search(r"\b(slika|slici|sliku|shem|crtež|crtez|dijagram|oscilogram|skic)",
                       q["question"], re.I) or q.get("figure_options"))]
print(f"questions naming a figure  : {len(want)}")
print(f"found by ink alone         : {len(found_by_ink)} {sorted(found_by_ink)}")
print(f"figures cropped            : {len(made)}")
print(f"missing                    : {sorted(set(want) - set(made))}")
# Measured from disk, not from the stat() taken inside postprocess() right after PIL.save():
# on Windows that reads a directory entry the write has not yet updated, and under-reported
# the total by better than tenfold.
print(f"total size                 : "
      f"{sum((FIGS / v['file']).stat().st_size for v in made.values()) // 1024} KB")
