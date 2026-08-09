"""Parse the HRS A-class banks via PyMuPDF, capturing text, colour and layout.

Correct answers are marked by red text in the source PDFs (#ff0000 / #c00000).
PyMuPDF also recovers the Croatian diacritics that pdftotext destroys.
"""
import json, re
from pathlib import Path
import pymupdf

DOCS = Path(r"g:/My Drive/Electronics/HAM Radio License/docs")
OUT = Path(__file__).parent
BANKS = [
    ("tehnicki", "RA_ispiti_9_A_razred_Tehnicki_dio.pdf",             "teh"),
    ("propisi",  "RA_ispiti_8_A_razred_HR_i_medjunarodni_propisi.pdf","pro"),
    ("pravila",  "RA_ispiti_7_A_razred_Pravila_i_postupci.pdf",       "prv"),
]

# Symbol-font glyphs land in the Unicode private-use area; Adobe Symbol encoding.
SYMBOL = {0xF057: "Ω", 0xF06C: "λ", 0xF06D: "μ",
          0xF070: "π", 0xF044: "Δ", 0xF032: "2"}

# The source sets these headings letter-spaced ("K O M P O N E N T E"); canonicalise.
SUBSECTIONS = {
    1: "Električna, elektromagnetska i radijska teorija",
    2: "Komponente",
    3: "Krugovi",
    4: "Prijamnici",
    5: "Odašiljači (predajnici)",
    6: "Antene i antenski vodovi",
    7: "Rasprostiranje elektromagnetskog vala",
    8: "Mjerenja",
    9: "Smetnje i imunitet",
    10: "Električna sigurnost",
}

Q_RE   = re.compile(r"^(\d{1,3})\.\s*(.*)$")
OPT_RE = re.compile(r"^\(?([a-h])[).]\s*(.*)$")
HEAD   = re.compile(r"^(\d{1,2})\.\s+([^a-z]{6,})$")


def is_red(c: int) -> bool:
    r, g, b = (c >> 16) & 255, (c >> 8) & 255, c & 255
    return r > 100 and r - g > 50 and r - b > 50


def clean(s: str) -> str:
    s = s.replace("\u00f1", "\u0111").replace("\u00d1", "\u0110")   # ñ -> đ
    for code, ch in SYMBOL.items():
        s = s.replace(chr(code), ch)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r",,\s*(.+?)\s*[\"'\u201c\u201d]", "\u201e\\1\u201c", s)
    return s.strip().rstrip(",;")


def cells(page):
    """Return page content as cells: (x0, text, red, ymid).

    Options are laid out in two columns, so we read the left column top-to-bottom
    and then the right column, rather than row-major -- otherwise fragments of
    "a) Paralelni titrajni krug" and "c) niskopropusni filtar" interleave.
    """
    raw = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            spans = [s for s in ln["spans"] if s["text"].strip()]
            if not spans:
                continue
            x0, y0, x1, y1 = ln["bbox"]
            raw.append([x0, "".join(s["text"] for s in spans),
                        any(is_red(s["color"]) for s in spans), (y0 + y1) / 2, x1])

    # Fragments on one baseline overlap by a character or two ("...24 GHz" + "z. Koliki"),
    # so join them with de-duplication. A fragment starting a new option, or separated by
    # a wide gap, begins a new cell -- that is the second option column.
    # Cluster baselines with a tolerance -- fixed buckets split fragments that sit
    # 1pt apart but belong to the same visual line.
    rows: list[list] = []
    for c in sorted(raw, key=lambda c: c[3]):
        if rows and c[3] - rows[-1][0][3] < 4.0:
            rows[-1].append(c)
        else:
            rows.append([c])

    out = []
    for frags in rows:
        frags.sort(key=lambda c: c[0])
        cur = None
        for x0, text, red, ym, x1 in ((f[0], f[1], f[2], f[3], f[4]) for f in frags):
            if cur is not None and not OPT_RE.match(text.strip()) and x0 - cur[4] < 14:
                if x0 < cur[4]:                       # overlapping: drop the repeated glyphs
                    for k in (3, 2, 1):
                        if cur[1][-k:] == text[:k]:
                            text = text[k:]
                            break
                    cur[1] += text
                else:
                    cur[1] += " " + text
                cur[2] = cur[2] or red
                cur[4] = max(cur[4], x1)
            else:
                cur = [x0, text, red, ym, x1]
                out.append(cur)
    out.sort(key=lambda c: (round(c[3] / 4), c[0]))
    return [c[:4] for c in out]


def parse(pdf: Path, section: str, prefix: str):
    doc = pymupdf.open(pdf)
    qs, cur, sub = [], None, None

    # Learn where option columns start in this document.
    tally: dict[int, int] = {}
    for page in doc:
        for x0, text, _, _ in cells(page):
            if OPT_RE.match(text.strip()):
                tally[round(x0)] = tally.get(round(x0), 0) + 1
    colx = [x for x, n in tally.items() if n >= 2]

    def flush():
        if cur:
            qs.append(cur)

    for pno, page in enumerate(doc):
        for x0, text, red, _ in cells(page):
            t = text.strip()
            if not t or re.fullmatch(r"\d{1,3}", t):
                continue

            if section == "tehnicki" and HEAD.match(t) and not OPT_RE.match(t):
                flush(); cur = None
                m = HEAD.match(t)
                n = int(m.group(1))
                sub = f"{n}. {SUBSECTIONS.get(n, clean(m.group(2)).title())}"
                continue

            # A bare "N." cell followed by an ALL-CAPS cell is a section heading,
            # not question N (e.g. "6." + "ANTENE I ANTENSKI VODOVI").
            if section == "tehnicki" and cur is not None and not cur["opts"] \
               and not cur["question"].strip() and t.isupper() and len(t) > 5:
                n = cur["number"]
                sub = f"{n}. {SUBSECTIONS.get(n, clean(t).title())}"
                cur = None
                continue

            q, opt = Q_RE.match(t), OPT_RE.match(t)
            if q and not opt and (not q.group(2) or not OPT_RE.match(q.group(2))):
                flush()
                cur = {"number": int(q.group(1)), "section": section, "subsection": sub,
                       "question": q.group(2), "opts": {}, "red": set(),
                       "cols": {}, "page": pno + 1}
                continue
            if cur is None:
                continue

            # Real options always start at one of the option-column x positions.
            # This rejects "(f)" embedded in "Frekvencija (f)." and stray fragments
            # like "a." that would otherwise open a bogus option.
            if opt and (opt.group(1) in cur["opts"]
                        or not any(abs(x0 - cx) < 6 for cx in colx)):
                opt = None

            if opt:
                lbl, body = opt.group(1), opt.group(2)
                cur["opts"][lbl] = cur["opts"].get(lbl, "") + " " + body
                cur["cols"][round(x0 / 120)] = lbl
                if red:
                    cur["red"].add(lbl)
            elif cur["opts"]:
                # continuation: attach to the last option started in this column
                key = min(cur["cols"], key=lambda k: abs(k - round(x0 / 120)))
                lbl = cur["cols"][key]
                cur["opts"][lbl] += " " + t
                if red:
                    cur["red"].add(lbl)
            else:
                cur["question"] += " " + t
                if red:
                    cur["red"].add("?")
    flush()

    out = []
    for q in qs:
        # an option must carry actual content, not just stray punctuation
        q["opts"] = {k: v for k, v in q["opts"].items()
                     if re.search(r"[0-9A-Za-zČĆŽŠĐčćžšđΩλμπΔ]", clean(v))}
        labels = sorted(q["opts"])
        relabelled = None
        if len(labels) == 4 and set(labels) != set("abcd"):
            relabelled = labels
            opts = {t: clean(q["opts"][s]) for t, s in zip("abcd", labels)}
            red = {t for t, s in zip("abcd", labels) if s in q["red"]}
        else:
            opts = {k: clean(v) for k, v in q["opts"].items()}
            red = set(q["red"])
        red.discard("?")
        out.append({
            "id": f"{prefix}-{q['number']:03d}",
            "section": q["section"], "subsection": q["subsection"],
            "number": q["number"], "page": q["page"],
            "question": clean(q["question"]), "options": opts,
            "answer": sorted(red)[0] if len(red) == 1 else None,
            "red_marks": sorted(red), "relabelled_from": relabelled,
            "answer_source": "hrs-red" if len(red) == 1 else None,
            "explanation": None, "citation": None,
            "status": "extracted" if len(red) == 1 else "needs_review",
            "sources": ["hrs"],
        })
    return out


def apply_overrides(qs: list[dict]) -> list[dict]:
    ov = json.loads((OUT / "overrides.json").read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in qs}

    for spec in ov["split"]:
        src = by_id[spec["from"]]
        new = dict(src)
        n = spec["new"]
        new.update(id=n["id"], number=n["number"], question=n["question"],
                   options={t: src["options"][s] for t, s in zip("abcd", n["take_options"])
                            if s in src["options"]},
                   note=n["note"], status="extracted")
        new["answer"] = next((t for t, s in zip("abcd", n["take_options"])
                              if s in src["red_marks"]), None)
        new["red_marks"] = [new["answer"]] if new["answer"] else []
        src["options"] = {k: v for k, v in src["options"].items()
                          if k in spec["keep_options"]}
        src["red_marks"] = [r for r in src["red_marks"] if r in spec["keep_options"]]
        src["answer"] = src["red_marks"][0] if len(src["red_marks"]) == 1 else None
        src["status"] = "extracted" if src["answer"] else "needs_review"
        qs.insert(qs.index(src) + 1, new)

    by_id = {q["id"]: q for q in qs}          # refresh: splits added new ids
    for qid, patch in ov["patch"].items():
        for key, val in patch.items():
            if key.startswith("options."):
                by_id[qid]["options"][key.split(".", 1)[1]] = val
            elif key == "question":
                by_id[qid]["question"] = val

    for qid, spec in ov["figure_options"].items():
        q = by_id.get(qid)
        if q:
            q["figure_options"] = True
            q["answer"] = spec["answer"]
            q["options"] = dict(spec["options"])
            q["status"] = "extracted"
            q["answer_source"] = "hrs-red"
    return qs


allq = []
for section, fname, prefix in BANKS:
    p = parse(DOCS / fname, section, prefix)
    nums = [q["number"] for q in p]
    gaps = sorted(set(range(1, max(nums) + 1)) - set(nums))
    n4 = sum(len(q["options"]) == 4 for q in p)
    n1 = sum(q["answer"] is not None for q in p)
    print(f"{section:9s} q={len(p):4d} gaps={gaps or '-':<12} "
          f"4-options={n4}/{len(p)}  single-red-answer={n1}/{len(p)}")
    bad = [q["id"] for q in p if q["answer"] is None or len(q["options"]) != 4]
    if bad:
        print(f"          needs review: {bad}")
    allq += p

allq = apply_overrides(allq)
(OUT / "bank.json").write_text(json.dumps(allq, ensure_ascii=False, indent=2), encoding="utf-8")

unresolved = [q["id"] for q in allq
              if q["answer"] is None
              or (len(q["options"]) != 4 and not q.get("figure_options"))]
print(f"\nafter overrides: total {len(allq)}  "
      f"answered={sum(q['answer'] is not None for q in allq)}  "
      f"unresolved={unresolved or 'none'}")
