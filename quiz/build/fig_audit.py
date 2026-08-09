"""Audit which book questions still need a STEM figure, and propose crop windows.

Only 6 of the 720 book questions carry a `figure`, and all six are questions whose
OPTIONS are pictures (`figure_is_options`). Stem figures -- a schematic, curve or
oscillogram sitting between the stem and normal text options -- were never in scope,
so a stem like "Sklop na slici je:" renders with nothing to look at. `bk-teh-5-60`
(item 0030) was the pilot fix for exactly this; this script finds the rest of them.

Two independent detectors, neither sufficient alone:
  * NAME   -- the stem itself names a figure ("na slici", "prema shemi", "kao na
              skici", ...augmented with a handful of book-specific words --
              krivulja/graf/prikaz/zaslon/spektar/tlocrt/simbol -- that the exam
              bank's own figures2.py never needed).
  * GAP    -- the vertical gap between the stem's own y and the topmost option's y,
              read straight off book_parsed2.json, exceeds GAP_THRESHOLD points. This
              is the stronger detector: it catches stems that never say "slici" at
              all, e.g. bk-teh-5-11 ("Koliki je napon U.?"), because the picture is
              still sitting in the gap even though nothing points at it in words.

Both detectors only run over questions the coordinate parser (parse_book2.py) already
recovered with real geometry (`y` and `opts` populated) -- the handful of questions
that exist only as eye-transcribed book_overrides.json entries (the 6 figure-options
ones) have no geometry to measure and are reported separately, from `has_figure`.

For every suspect lacking a figure, a crop window `[y0, y1]` (PDF points, page-width)
is proposed by re-reading the page directly with pymupdf: `y0` is the bottom of the
stem's own last line (located by fuzzy-matching the KNOWN stem text, already parsed
correctly, against the page's raw OCR lines -- this survives the OCR gluing a stray
figure-caption glyph onto an otherwise-real line, the same bug item 0030 found and
fixed by hand for bk-teh-5-60). `y1` is where the next thing after the figure starts,
by one of three rules depending on how many of the four options are real text rather
than a bare picture label -- see find_next_marker()'s docstring.

This is a PROPOSAL tool. It writes fig_windows.json for a human to look at in items
0032-0037; it never touches book_overrides.json itself. Its only enforcement power is
a regression gate: if a question book_overrides.json already says has a figure loses
its entry in figs_book_index.json (i.e. book_figures.py silently stopped cropping it),
this script exits nonzero so rebuild.py aborts rather than ship the regression quietly.
"""
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf

OUT = Path(__file__).parent
PDF = Path(r"g:/My Drive/Electronics/HAM Radio License/docs/Radiokomunikacije_ocr.pdf")

GAP_THRESHOLD = 60        # pt; stem-y to first-option-y gap above this signals a figure
NOMINAL_LINE_HEIGHT = 13.0  # pt; typical single-line height in this book's OCR text layer
MAX_LINE_HEIGHT = 20.0      # pt; above this a line's own bbox is OCR noise, not real height
STEM_MATCH_RATIO = 0.55     # difflib ratio to accept a page line as (noisy) stem text
OPTION_MATCH_RATIO = 0.6    # difflib ratio to accept a page line as a known option's text
CALIBRATION_BAR = 10        # pt; item 0031's own "not usable past this" tolerance

FIGURE_WORD = re.compile(
    r"\b(slika|slici|sliku|shem|crte\u017e|crtez|dijagram|oscilogram|skic"
    r"|krivulj|graf|prikaz|zaslon|spektar|tlocrt|simbol)", re.I)
NEXT_ANCHOR = re.compile(r"^\(?(\d{1,3})\s*[.,;:]")

doc = pymupdf.open(PDF)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.replace("\u0111", "d"))


def page_lines(page):
    out = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            t = "".join(s["text"] for s in ln["spans"])
            if t.strip():
                out.append((ln["bbox"][1], ln["bbox"][3], ln["bbox"][0], t))
    return sorted(out, key=lambda c: (c[0], c[2]))


def is_numcol(x, t):
    """A question-number anchor, real or OCR-mangled ("s2." for "52.", "u." for
    "11."). Requires a digit (or the two known letter-only mangles) so that a bare
    figure-caption glyph like "A" sitting in the same left margin is not mistaken
    for one -- 4-36's diagram labels sit at x<80 too, and have no digit in them.
    """
    tt = t.strip()
    if not (x < 80 and len(tt) <= 6):
        return False
    # A digit somewhere is the normal case; "u"/"u." is parse_book2.py's own
    # documented OCR misreading of "11." (the pair reads as a single 'u' glyph).
    # Nothing looser than that: a bare "i" or "A" is exactly what a figure's own
    # stray caption glyph looks like at this same left margin (bk-teh-4-36's "i"
    # and "A" fragments sit at x<80 too), and must NOT be read as a next-question
    # anchor.
    return bool(re.search(r"\d", tt)) or tt.lower().strip(".") == "u"


def find_stem(L, nstem, y_hint):
    """Where this question's stem starts and ends among the page's OWN OCR lines.

    Matches the ALREADY-KNOWN stem text (from book_parsed2.json or
    book_overrides.json, both independently correct) against the page's raw text,
    line by line, via a difflib ratio rather than exact equality -- the OCR layer
    routinely glues a stray figure-caption glyph onto an otherwise-real line
    ("preko voda mrežnog napajanja? IH", the "IH" being the figure's, not the
    stem's; see book_figures.py's docstring on bk-teh-5-60 for the same bug).
    A whole matched line's length (not just its matching prefix) is consumed from
    the running position in `nstem`, so a noisy tail does not desynchronise the
    match against the next line.
    """
    pos = 0
    top = bot = last_top = None
    started = y_hint is None
    for y0, y1, x, t in L:
        if not started:
            if y0 < y_hint - 2:
                continue
            started = True
        if pos == 0 and not is_numcol(x, t):
            # Haven't found the stem's first line yet: skip anything (earlier
            # questions' text, stray glyphs) that doesn't even start matching, rather
            # than giving up on the very first line tried -- relevant when y_hint is
            # None and the scan starts from the top of the page.
            nt = norm(t)
            if not (nt and difflib.SequenceMatcher(
                    None, nt[:10], nstem[:10]).ratio() >= STEM_MATCH_RATIO):
                continue
        if is_numcol(x, t):
            continue
        if pos >= len(nstem):
            break
        nt = norm(t)
        if not nt:
            continue
        window = nstem[pos:pos + len(nt)]
        ratio = difflib.SequenceMatcher(None, nt, window).ratio() if window else 0
        if ratio >= STEM_MATCH_RATIO:
            pos += len(nt)
            top = top if top is not None else y0
            bot, last_top = y1, y0
        else:
            break
    coverage = pos / len(nstem) if nstem else 0
    if bot is not None and (bot - last_top) > MAX_LINE_HEIGHT:
        # This LAST line's own bbox is OCR noise (a scanned blank strip mis-measured
        # as 47pt tall, bk-teh-2-20's "IH" line is the ground-truth example) -- fall
        # back to a nominal single-line height instead of trusting it. Checked
        # against the last consumed line's OWN top, not the stem's overall top, so a
        # normal multi-line stem is not mistaken for noise merely by spanning >20pt.
        bot = last_top + NOMINAL_LINE_HEIGHT
    return top, bot, coverage


def find_next_marker(L, after_y, options):
    """y where the figure's own extent ends -- the far edge of the crop window.

    Three cases, distinguished by how many of the four options are REAL text
    (>=6 normalised chars) rather than a bare picture label ("a)"):
      * all four real   -- normal text options sit right after the figure (e.g.
                            bk-teh-5-60): stop at the TOP of the first one, so the
                            crop excludes the options themselves.
      * some real (1-3) -- a figure-options question whose one textual choice is
                            laid out as part of the same picture block (bk-teh-2-46:
                            three oscillogram thumbnails, one "(d) ni jedan od
                            prikazanih" text line): stop just BELOW that line, so
                            the crop keeps the textual choice legible.
      * none real       -- pure picture options; nothing to anchor on but the next
                            question's own number, so stop just above it.
    """
    real = [norm(v) for v in options.values() if len(norm(v)) >= 6]
    real_hits = []
    anchor_y = None
    for y0, y1, x, t in L:
        if y0 <= after_y:
            continue
        tt = t.strip()
        if anchor_y is None and (is_numcol(x, t) or NEXT_ANCHOR.match(tt)):
            anchor_y = y0
        nt = norm(t)
        if nt and len(nt) >= 6:
            for ro in real:
                if (ro in nt or nt in ro
                        or difflib.SequenceMatcher(None, nt, ro).ratio() >= OPTION_MATCH_RATIO):
                    real_hits.append((y0, y1))
                    break
    if len(real) == 4 and real_hits:
        return min(y0 for y0, _ in real_hits) - 1, "option-top"
    if 0 < len(real) < 4 and real_hits:
        return max(y1 for _, y1 in real_hits) + 5, "option-bottom+5"
    if anchor_y is not None:
        return anchor_y - 2, "next-anchor"
    return None, "none"


def propose_window(page_no, question, options, y_hint=None):
    """[y0, y1] PDF-point crop window, or (None, coverage, None) if the stem's own
    text could not be located on the page at all (should not happen for anything
    this script's own candidate list produces -- it means the page/question given
    do not agree, and no window should be trusted)."""
    page = doc[page_no - 1]
    L = page_lines(page)
    nstem = norm(question)
    top, bot, coverage = find_stem(L, nstem, y_hint)
    if bot is None:
        return None, coverage, None
    y1, why = find_next_marker(L, bot, options)
    if y1 is None:
        # No option text and no next-question anchor on this page at all: the figure
        # runs to the bottom of the page. Fall back to just above the printed folio
        # number (figures2.py's own "page_floor" idea for a last-of-page question);
        # book_figures.py's postprocess() trims the resulting slack automatically.
        H = page.rect.height
        ys = [ly0 for ly0, ly1, lx, lt in L if ly0 > H * 0.85 and lt.strip().isdigit()]
        y1 = (min(ys) - 10) if ys else H - 40
        why = "page-floor"
    return [round(bot), round(y1)], coverage, why


def main():
    book = json.loads((OUT / "book_parsed2.json").read_text(encoding="utf-8"))
    ov = json.loads((OUT / "book_overrides.json").read_text(encoding="utf-8"))
    idx_path = OUT / "figs_book_index.json"
    figs_idx = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else {}

    has_figure = {qid for qid, spec in ov.items()
                  if not qid.startswith("_") and "figure" in spec}

    # --- regression gate ------------------------------------------------------
    if idx_path.exists():
        lost = sorted(qid for qid in has_figure if qid not in figs_idx)
        if lost:
            sys.exit(f"fig_audit: {len(lost)} question(s) with a figure in "
                      f"book_overrides.json have none in figs_book_index.json "
                      f"(book_figures.py stopped cropping them): {lost}")
        print(f"fig_audit: regression gate ok -- all {len(has_figure)} applied "
              f"figures still in figs_book_index.json")
    else:
        print("fig_audit: figs_book_index.json not built yet -- "
              "regression gate skipped (run this after book_figures.py)")

    # --- two detectors over the coordinate-parsed book questions ---------------
    candidates = []
    for q in book:
        if not q.get("opts") or not q.get("y"):
            continue  # eye-transcribed override (figure-options) -- no geometry here
        name_hit = bool(FIGURE_WORD.search(q["question"]))
        gap = min(o[0] for o in q["opts"]) - q["y"]
        gap_hit = gap > GAP_THRESHOLD
        if name_hit or gap_hit:
            candidates.append((q, name_hit, gap_hit, gap))
    candidates.sort(key=lambda c: (c[0]["section"], c[0]["skupina"], c[0]["num"]))

    print(f"\n{'id':14s} {'page':>4s} {'gap':>7s}  {'detector':<10s} figure")
    outstanding = {}
    unresolved = []
    for q, name_hit, gap_hit, gap in candidates:
        det = "name+gap" if name_hit and gap_hit else ("name" if name_hit else "gap")
        already = q["id"] in has_figure
        print(f"{q['id']:14s} {q['page']:>4d} {gap:>7.1f}  {det:<10s} "
              f"{'yes' if already else 'NO'}")
        if already:
            continue
        window, coverage, why = propose_window(q["page"], q["question"], q["options"],
                                                 y_hint=q["y"])
        if window is None:
            unresolved.append(q["id"])
            print(f"    ! stem text not located on page {q['page']} -- no window proposed "
                  f"(coverage {coverage:.0%})")
            continue
        outstanding[q["id"]] = window

    (OUT / "fig_windows.json").write_text(
        json.dumps(outstanding, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    n_name = sum(1 for _, nh, gh, _ in candidates if nh)
    n_gap = sum(1 for _, nh, gh, _ in candidates if gh)
    n_both = sum(1 for _, nh, gh, _ in candidates if nh and gh)
    n_already = sum(1 for q, *_ in candidates if q["id"] in has_figure)
    print(f"\nnames a figure   : {n_name}")
    print(f"gap > {GAP_THRESHOLD}pt      : {n_gap}")
    print(f"both             : {n_both}")
    print(f"union (suspects) : {len(candidates)}")
    print(f"already fixed    : {n_already}")
    print(f"unresolved       : {len(unresolved)} {unresolved}")
    print(f"proposed         : {len(outstanding)}  -> fig_windows.json")

    # --- validate the proposer against every window already applied by eye -----
    print("\ncalibration against ground truth (book_overrides.json windows):")
    by_id = {q["id"]: q for q in book}
    max_err = 0.0
    n_checked = 0
    for qid, spec in sorted(ov.items()):
        if qid.startswith("_") or "figure" not in spec:
            continue
        if spec.get("reason") == "cross-reference":
            # Not a fresh figure at all -- its stem says outright that the picture
            # belongs to an earlier question ("slika je iz 7. pitanja"), and its
            # book_overrides.json window is a copy of that question's, not anything
            # measured from bk-teh-4-08's own geometry. The proposer has nothing to
            # calibrate against here; a cross-reference has to be spotted by eye
            # (its stem naming another question number) and its window COPIED, not
            # proposed.
            print(f"  {qid:14s}  cross-reference (shares a figure with another "
                  f"question) -- not a fresh proposal, skipped")
            continue
        q = by_id.get(qid)
        y_hint = q["y"] if q and q.get("y") else None
        window, coverage, why = propose_window(spec["page"], spec["question"],
                                                 spec["options"], y_hint=y_hint)
        actual = spec["figure"]
        if window is None:
            print(f"  {qid:14s}  stem not located -- cannot calibrate")
            continue
        n_checked += 1
        err = max(abs(window[0] - actual[0]), abs(window[1] - actual[1]))
        max_err = max(max_err, err)
        flag = "" if err <= CALIBRATION_BAR else "  ** exceeds the ~10pt usability bar **"
        print(f"  {qid:14s} proposed {window!s:14s} actual {actual!s:14s} "
              f"delta {err:4.1f}pt  ({why}){flag}")
    print(f"\nworst calibration delta over {n_checked} known windows: {max_err:.1f}pt")


if __name__ == "__main__":
    main()
