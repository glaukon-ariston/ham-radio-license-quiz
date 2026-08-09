"""Crop the diagram-options of the book questions whose answers ARE pictures, and patch
in any stem text that book_overrides.json corrects by eye.

Six questions in the priručnik offer circuit schematics, filter curves or oscillograms
instead of option text, so there is nothing for a text parser to find. The crop windows
live in book_overrides.json as PDF-point y ranges, taken from the text layout: from just
below the stem to just above the next question.

Red neutralisation is reused from figures2.postprocess deliberately: this book also marks
some correct answers in red, and a crop that kept the red would hand over the answer.

A seventh kind of question (reason "figure-in-stem") parses fine on its own -- the
coordinate parser in parse_book2.py finds its number, stem and four text options without
help -- but a sketch sits between the stem and the options, and the sketch's own printed
label lives in the stem's x-column, so the parser's line-stitching glues it onto the stem
as if it were wrapped text (bk-teh-5-60's sketch labelled "8m" became a trailing
"... Potrebno je: 8m"). Because the question is already parsed, parse_book2.py's own
override-merge loop skips it (it only ADDS entries the parser missed entirely), so the
correction happens here instead: any override that carries a "question" is patched
straight into book_parsed2.json after parse_book2.py has already run, which is early
enough that rebuild.py still picks up the corrected text.
"""
import json
from pathlib import Path

import pymupdf

from figures2 import postprocess          # shared so the red rule cannot drift apart

OUT = Path(__file__).parent
PDF = Path(r"g:/My Drive/Electronics/HAM Radio License/docs/Radiokomunikacije_ocr.pdf")
DST = OUT / "figs_book"
DST.mkdir(exist_ok=True)

ov = json.loads((OUT / "book_overrides.json").read_text(encoding="utf-8"))
doc = pymupdf.open(PDF)
index = {}

for qid, spec in ov.items():
    if qid.startswith("_") or "figure" not in spec:
        continue
    y0, y1 = spec["figure"]
    page = doc[spec["page"] - 1]
    path = DST / f"{qid}.png"
    page.get_pixmap(clip=pymupdf.Rect(0, y0, page.rect.width, y1), dpi=150).save(path)
    w, h, _ = postprocess(path)
    index[qid] = {"file": path.name, "w": w, "h": h,
                  "is_options": bool(spec.get("figure_is_options"))}

json.dump(index, open(OUT / "figs_book_index.json", "w", encoding="utf-8"), indent=1)
size = sum((DST / v["file"]).stat().st_size for v in index.values())
print(f"book figures: {len(index)}   total {size // 1024} KB")

# Patch stem/option text for questions the coordinate parser already found on its own but
# read with OCR bleed from a figure caption. Only overrides that carry a "question" apply;
# ids the parser missed entirely are added by parse_book2.py's own loop, not here.
parsed_path = OUT / "book_parsed2.json"
by_id = {q["id"]: q for q in json.loads(parsed_path.read_text(encoding="utf-8"))}
patched = []
for qid, spec in ov.items():
    if qid.startswith("_") or "question" not in spec:
        continue
    q = by_id.get(qid)
    if q is None:
        continue                                   # not independently parsed; not our job
    if q["question"] != spec["question"] or q["options"] != spec["options"]:
        # num_source is left untouched: rebuild.py string-matches it against exactly
        # "ocr anchor" to decide whether the citation gets a "broj pitanja rekonstruiran"
        # suffix, and this patch corrects the STEM, not the number -- the anchor is real.
        q["question"] = spec["question"]
        q["options"] = spec["options"]
        q["text_patched"] = spec["reason"]
        patched.append(qid)
if patched:
    parsed_path.write_text(
        json.dumps(list(by_id.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"book stems patched from overrides: {patched}")
