"""Crop the diagram-options of the book questions whose answers ARE pictures.

Six questions in the priručnik offer circuit schematics, filter curves or oscillograms
instead of option text, so there is nothing for a text parser to find. The crop windows
live in book_overrides.json as PDF-point y ranges, taken from the text layout: from just
below the stem to just above the next question.

Red neutralisation is reused from figures2.postprocess deliberately: this book also marks
some correct answers in red, and a crop that kept the red would hand over the answer.
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
