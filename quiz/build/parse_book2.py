"""Parse the OCR'd priručnik using COORDINATES, not OCR reading order.

The page has three x-zones:
    x < 80    question numbers ("22.")
    x ~ 90    question stem and the left option column
    x ~ 307   the right option column
A question owns every line from its number's baseline down to the next number's.
Option letters OCR badly ("(€)" for "(c)"), so options are taken BY POSITION.
"""
import json, re, unicodedata
from pathlib import Path
import pymupdf

PDF = Path(r"g:/My Drive/Electronics/HAM Radio License/docs/Radiokomunikacije_ocr.pdf")
OUT = Path(__file__).parent
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6}
SECTIONS = {"tehnicki": (282, 348), "propisi": (351, 369), "pravila": (371, 402)}
PER = {"tehnicki": 60, "propisi": 20, "pravila": 40}

NUM  = re.compile(r"^\(?(\d{1,3})\s*[.,;:]?\)?$")
# The OCR sometimes runs the number and the stem together on a single line sitting in the
# NUMBER column ("3. — Amplituda nemoduliranog vala nositelja je 30 V, ..."). Such a line
# matches neither NUM nor the stem-x test, so it used to be discarded — and the question
# with it. It carries both an anchor and the stem, so it is the most valuable line there is.
MERGED = re.compile(r"^\(?(\d{1,3})\s*[.,;:]\s*[—–\-]*\s*(.{8,})$")
# ...and sometimes that merged line's number is itself misread ("I. Rad amaterske postaje
# može zabraniti:" for "1."). The stem is still worth recovering, but the number is only
# as trustworthy as the glyph, so it goes to the corroboration tier rather than the anchors.
MERGED_FUZZY = re.compile(r"^\(?([0-9IlSsOoBZgq|€$]{1,3})\s*[.,;:]\s*[—–\-]*\s*(.{8,})$")
OPT  = re.compile(r"^[(\[]?\s*[a-zA-Z\u20ac@\u00a9\u00ae]{1,2}\s*[)\].]\s*(.*)$")
SKUP = re.compile(r"SKUPINA\s+([IVX]+)", re.I)
INLINE_OPT = re.compile(r"\s*=?\s*[(\[]\s*[a-eč€@©®]\s*[)\]]\s*")
BARE_LABEL = re.compile(r"^[(\[]?\s*[a-zA-Z€@©®]{1,2}\s*[)\].]\s*$")
VERIFY = []   # (section, skupina, blocks, expected, anchors, interpolated)
CORROB = []   # (matches, mismatches) of glyph-repaired numbers vs the assignment

# The OCR misreads a handful of numbers as letters ("52." -> "s2.", "11." -> "u.").
# Repaired numbers are a SEPARATE, lower-confidence tier: they are never used to number
# a question, only to independently corroborate one that gap arithmetic already numbered.
FIX = str.maketrans({"s": "5", "S": "5", "$": "5", "l": "1", "I": "1", "i": "1",
                     "|": "1", "O": "0", "o": "0", "D": "0", "B": "8", "Z": "2",
                     "g": "9", "q": "9", "G": "6", "A": "4", "T": "7"})


def repaired_num(t: str):
    if t.strip() in ("u.", "u", "U."):
        return 11                       # the '11' pair reads as a single 'u' glyph
    s = t.strip().strip("().,;:")
    if not (1 <= len(s) <= 3):
        return None
    s = s.translate(FIX)
    return int(s) if s.isdigit() else None


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.replace("\u0111", "d"))


def lines(page):
    out = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            t = "".join(s["text"] for s in ln["spans"]).strip()
            if t:
                out.append((ln["bbox"][0], ln["bbox"][1], t))
    return sorted(out, key=lambda c: (c[1], c[0]))


def number_skupina(bucket, anchors, repairs):
    """Assign question numbers to the blocks of the skupina that just ended.

    Numbers come from OCR anchors, plus interpolation into gaps that are arithmetically
    forced (see below). Anything not forced is left unnumbered and therefore dropped,
    rather than guessed: an inferred number reads the WRONG ROW of the answer key, which
    is worse than a missing question.
    """
    todo = list(bucket)
    if not todo:
        return
    todo.sort(key=lambda q: (q["page"], q["y"]))
    for q in todo:
        for key, pool in (("anchor", anchors), ("repaired", repairs)):
            near = [n for (pno, y, n) in pool
                    if pno + 1 == q["page"] and abs(y - q["y"]) < 14]
            if len(near) == 1:
                q[key] = near[0]

    expected = PER[todo[0]["section"]]
    n = len(todo)
    raw = [(i, q["anchor"]) for i, q in enumerate(todo) if "anchor" in q]
    for i, num in raw:
        todo[i]["num"], todo[i]["num_source"] = num, "ocr anchor"

    # Blocks appear in document order and question numbers increase, so a block's number
    # can only ever run AHEAD of its position, by exactly the number of blocks the parser
    # dropped before it. That bounds the offset to [0, expected - n] and makes the whole
    # sequence analysable. If the parser had instead SPLIT or MERGED blocks the reasoning
    # would not hold — a surplus of blocks is the tell, so bail out on it.
    if n > expected:
        VERIFY.append((todo[0]["section"], todo[0]["skupina"], n, expected, len(raw), 0))
        CORROB.extend((q["repaired"] == q.get("num")) for q in todo if "repaired" in q
                      and "anchor" not in q)
        return

    slack = expected - n
    cand = [(i, a) for i, a in raw if i + 1 <= a <= i + 1 + slack and a <= expected]

    # Longest run of anchors with non-decreasing offset. A misread number ("u." -> 11)
    # breaks monotonicity, so this discards it instead of letting it corrupt a gap.
    best: list[int] = []
    for k in range(len(cand)):
        chain = [k]
        for m in range(k + 1, len(cand)):
            i, a = cand[chain[-1]]
            j, b = cand[m]
            if b > a and b - a >= j - i:          # offset non-decreasing
                chain.append(m)
        if len(chain) > len(best):
            best = chain
    keep = [cand[k] for k in best]

    # Interpolate a gap only when it is FORCED: the number of unnumbered blocks between
    # two kept anchors must equal the count of numbers missing between them, in which case
    # exactly one assignment is possible. Any drop inside the gap breaks the equality and
    # the gap is left alone.
    def fill(lo_i, lo_n, hi_i, hi_n):
        if hi_i - lo_i - 1 != hi_n - lo_n - 1:
            return 0
        for k in range(lo_i + 1, hi_i):
            todo[k]["num"] = lo_n + (k - lo_i)
            todo[k]["num_source"] = "interpolated (gap arithmetically forced)"
        return hi_i - lo_i - 1

    filled = 0
    if keep:
        filled += fill(-1, 0, keep[0][0], keep[0][1])                  # head of skupina
        for (i, a), (j, b) in zip(keep, keep[1:]):
            filled += fill(i, a, j, b)
        filled += fill(keep[-1][0], keep[-1][1], n, expected + 1)      # tail of skupina
    VERIFY.append((todo[0]["section"], todo[0]["skupina"], n, expected, len(keep), filled))

    # Corroboration: where the OCR produced a MANGLED number that glyph repair recovers,
    # compare it against what gap arithmetic independently concluded. The two rest on
    # unrelated evidence — glyph shape versus block counting — so agreement is a real
    # check on the interpolation, not a restatement of it.
    CORROB.extend((q["repaired"] == q.get("num")) for q in todo
                  if "repaired" in q and "anchor" not in q and "num" in q)


def parse():
    doc = pymupdf.open(PDF)
    out = []
    for section, (p0, p1) in SECTIONS.items():
        skupina, cur = 1, None
        bucket, anchors, repairs = [], [], []
        mark_y = None   # baseline of the most recent number seen in the number column
        start = 0    # index in bucket where the current skupina's blocks begin

        def close():
            if cur and cur["opts"]:
                bucket.append(cur)

        for pno in range(p0, p1 + 1):
            L = lines(doc[pno])
            # Margins alternate between recto and verso, so find the columns per page.
            # Only options that actually carry TEXT may define a column. A bare label
            # ("(a)", "b)") is a position, not a column, and so is a misread number like
            # "u."; letting either vote put the column on top of the NUMBER column.
            ox = sorted(x for x, y, t in L
                        if OPT.match(t) and OPT.match(t).group(1).strip())
            if not ox:
                continue
            # The right-hand option column is not at one fixed x: a figure beside the
            # options shifts it, and the shift varies question by question down the page.
            # A single median plus a tight tolerance therefore lost whole columns, leaving
            # questions with two options that were then discarded. Cluster instead, and
            # accept an option that lands near ANY column the page actually uses.
            cols: list[list[float]] = []
            for v in ox:
                if cols and v - cols[-1][-1] < 25:
                    cols[-1].append(v)
                else:
                    cols.append([v])
            # A misread number such as "u." (for "11.") also matches the option pattern, and
            # as a one-member cluster it declared the NUMBER column to be an option column —
            # which then suppressed its own repair. Every question 11 in the book was lost to
            # that circularity. Dense clusters locate the real left-hand column; anything to
            # the LEFT of it is number-column noise, while sparse clusters to its right are
            # genuine option columns shifted by a figure and must be kept.
            dense = [c for c in cols if len(c) >= 3] or cols
            # ...and "leftmost dense" is not enough either: a page can carry three or four
            # bare labels ("b)", "c)", "d)", text emitted elsewhere) in the number column,
            # which out-lefts the real column. Require a cluster to be at least half as
            # populated as the biggest before it may define the stem column.
            floor = max(len(c) for c in dense) / 2
            stem_x = next(sum(c) / len(c) for c in dense if len(c) >= floor)
            colx = [sum(c) / len(c) for c in cols if sum(c) / len(c) >= stem_x - 8]

            # Some questions set each option on its own full-width line, with only the
            # LABEL in the number column ("(a)" at x=64, its text at x=93). The label's
            # baseline sits a point or two BELOW its own text, so stitch each stray label
            # onto the nearest stem-x line; otherwise every such option reads as more stem
            # and the question ends up with none.
            taken, drop = set(), set()
            for i, (lx, ly, lt) in enumerate(L):
                if not (lx < stem_x - 8 and BARE_LABEL.match(lt)
                        and repaired_num(lt) is None):
                    continue
                best = min((j for j, (bx, by, _) in enumerate(L)
                            if j not in taken and abs(bx - stem_x) < 14
                            and abs(by - ly) < 6),
                           key=lambda j: abs(L[j][1] - ly), default=None)
                if best is not None:
                    bx, by, bt = L[best]
                    L[best] = (bx, by, f"{lt.strip()} {bt}")
                    taken.add(best)
                    drop.add(i)
            if drop:
                L = [c for i, c in enumerate(L) if i not in drop]

            for x, y, t in L:
                m = SKUP.search(t)
                if m and m.group(1).upper() in ROMAN:
                    close(); cur = None
                    number_skupina(bucket[start:], anchors, repairs)
                    start, anchors, repairs = len(bucket), [], []
                    skupina = ROMAN[m.group(1).upper()]
                    continue

                # The OCR drops many numbers entirely ("7." "8." "9." simply absent) and
                # mangles others ("u." for "11."), so a number cannot be REQUIRED to start a
                # question. But when one IS present it is decisive, so its baseline is kept
                # in mark_y and forces a block boundary below. Without that, a question whose
                # predecessor was still short of four options got absorbed into it, stem and
                # all, and both were lost to the four-option filter.
                forced_stem = False
                if x < stem_x - 8:
                    if len(t) <= 5:
                        n = NUM.match(t)
                        if n:
                            v = int(n.group(1))
                            if 1 <= v <= PER[section]:
                                anchors.append((pno, y, v))
                                mark_y = y
                            continue
                        r = repaired_num(t)
                        # The guard rejects a stray option label sitting in the number
                        # column — but it must be tied to an option COLUMN, not to the
                        # regex alone: "u." (the OCR's rendering of "11.") also matches
                        # OPT, so an unconditional test silently killed every question 11.
                        if r is not None and not (OPT.match(t) and
                                                  any(abs(x - c) < 14 for c in colx)):
                            if 1 <= r <= PER[section]:
                                repairs.append((pno, y, r))
                                mark_y = y
                            continue
                    else:
                        m = MERGED.match(t)
                        if m and re.search(r"[a-zžšđčć]{3}", m.group(2)):
                            anchors.append((pno, y, int(m.group(1))))
                            t, forced_stem, mark_y = m.group(2).strip(), True, y
                        else:
                            m = MERGED_FUZZY.match(t)
                            r = repaired_num(m.group(1) + ".") if m else None
                            if (m and r is not None
                                    and re.search(r"[a-zžšđčć]{3}", m.group(2))
                                    and m.group(2)[0].isupper()):
                                repairs.append((pno, y, r))
                                t, forced_stem, mark_y = m.group(2).strip(), True, y

                o = OPT.match(t)
                near_col = any(abs(x - c) < 14 for c in colx)
                is_stem = forced_stem or ((-10 < (x - stem_x) < 26) and not o)

                if o and near_col and not forced_stem:
                    if cur is None:
                        continue
                    body = o.group(1).strip().rstrip(",;.")
                    # The two option columns are sometimes flattened onto ONE line, with the
                    # column gap read as "=" ("devijaciju ... nositelja = (d) promjenu ...").
                    # Left unsplit this is one option instead of two, and the question is
                    # then discarded for having three.
                    parts = [p.strip().rstrip(",;.") for p in INLINE_OPT.split(body)]
                    # Only trust the split when it yields exactly two substantial halves.
                    # Option text legitimately contains parenthesised letters ("točka (A)",
                    # "Frekvencija (f)"), and splitting on those destroys real options.
                    if len(parts) == 2 and all(len(p) >= 6 for p in parts):
                        for p in parts:
                            cur["opts"].append((y, x, p))
                    else:
                        cur["opts"].append((y, x, body))
                elif (cur is not None and cur["opts"] and cur["opts"][-1][2] == ""
                      and abs(y - cur["opts"][-1][0]) < 5 and x > cur["opts"][-1][1]
                      and len(t) < 30 and not t.rstrip().endswith(":")):
                    # An option label whose text the OCR emitted as a separate fragment on
                    # the same baseline ("(d)" then "250 Hz" as its own line). Bounded by
                    # length and by the trailing colon, because without those guards this
                    # branch swallowed stems that merely happened to follow an empty label.
                    yy, xx, _ = cur["opts"][-1]
                    cur["opts"][-1] = (yy, xx, t.strip().rstrip(",;."))
                elif is_stem:
                    # A new question starts when the CURRENT one is already complete
                    # (four options). Keying on stem length instead lost short stems
                    # such as "Radioamater je::" (16 chars) and cost whole blocks.
                    # A number's baseline often falls BETWEEN the two lines of its own
                    # wrapped stem ("Klupska amaterska postaja…" / "lokaciji radi dulje
                    # od:"), so the mark may only split once options have started —
                    # otherwise it cuts a stem in half.
                    numbered_here = (mark_y is not None and abs(y - mark_y) < 14
                                     and (cur is None or cur["opts"]))
                    if numbered_here:
                        mark_y = None                # a mark starts exactly one question
                    if cur is not None and (len(cur["opts"]) >= 4 or numbered_here
                                            or forced_stem):
                        close()
                        cur = None
                    if cur is None:
                        # The last option of the question that just closed may itself wrap
                        # onto the next line, which lands at stem x. A stem always opens
                        # with a capital, so a lowercase line here belongs to that option —
                        # without this it was glued onto the NEXT question's stem
                        # ("neznatno oslabljeni Koje područje ionosfere...").
                        if (bucket and not forced_stem and re.match(r"[a-zćčžšđ]", t)
                                and bucket[-1]["opts"]):
                            yy, xx, txt = bucket[-1]["opts"][-1]
                            bucket[-1]["opts"][-1] = (yy, xx, txt + " " + t)
                            continue
                        if len(t) < 10 or not re.search(r"[a-zžšđčć]", t):
                            continue                     # figure label or stray glyph
                        cur = {"section": section, "skupina": skupina, "question": t,
                               "opts": [], "page": pno + 1, "y": y}
                    elif cur["opts"]:                    # wrapped option text
                        yy, xx, txt = cur["opts"][-1]
                        cur["opts"][-1] = (yy, xx, txt + " " + t)
                    else:
                        cur["question"] += " " + t
                # anything else (figure labels, stray glyphs) is ignored
        close()
        number_skupina(bucket[start:], anchors, repairs)
        out += bucket

    # order options by row then column, then assign a..d positionally
    keep = []
    for q in out:
        opts = sorted(q["opts"], key=lambda o: (round(o[0] / 9), o[1]))
        texts = [t for _, _, t in opts if t]
        if len(texts) != 4 or not q["question"] or "num" not in q or q["num"] > PER[q["section"]]:
            continue
        q["options"] = dict(zip("abcd", texts))
        q["norm"] = norm(q["question"])
        keep.append(q)
    return keep


qs = parse()
keys = json.loads((OUT / "book_keys.json").read_text(encoding="utf-8"))
ROM = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}
SEC = {"teh": "tehnicki", "pro": "propisi", "pra": "pravila"}
cols = keys["_columns"]

final = []
for q in qs:
    row = keys[q["section"]].get(str(q["num"]))
    if not row:
        continue
    q["answer"] = row[cols.index(ROM[q["skupina"]])].lower()
    q["id"] = f"bk-{q['section'][:3]}-{q['skupina']}-{q['num']:02d}"
    final.append(q)

# Questions the coordinate parser cannot reach — two questions run together with no number
# between them, options set in one column instead of two, or options that are diagrams and
# have no text at all. These were read off the rendered page BY EYE. Only the wording and
# the option ORDER come from here; the ANSWER still comes from the book's own key table,
# so a transcription slip cannot invent an answer, it can only mis-order the options.
have = {q["id"] for q in final}
ov = json.loads((OUT / "book_overrides.json").read_text(encoding="utf-8"))
added = 0
for qid, spec in ov.items():
    if qid.startswith("_") or qid in have:
        continue
    _, sec, sk, num = qid.split("-")
    section, skupina, n = SEC[sec], int(sk), int(num)
    row = keys[section].get(str(n))
    if not row:
        continue
    q = {"section": section, "skupina": skupina, "num": n, "page": spec["page"],
         "question": spec["question"], "options": spec["options"], "y": 0,
         "opts": [], "num_source": f"read by eye ({spec['reason']})",
         "norm": norm(spec["question"]),
         "answer": row[cols.index(ROM[skupina])].lower(), "id": qid}
    for k in ("figure", "figure_is_options"):
        if k in spec:
            q[k] = spec[k]
    final.append(q)
    added += 1
print(f"overrides read by eye: +{added} "
      f"({sum(1 for k, v in ov.items() if not k.startswith('_') and k in have)} already parsed)")

from collections import Counter
ids = Counter(x["id"] for x in final)
ok = sum(1 for c in CORROB if c)
print(f"glyph-repaired numbers vs gap arithmetic: {ok}/{len(CORROB)} agree "
      f"(independent corroboration of interpolation)\n")
print("numbering (blocks/expected, anchors kept, gaps forced):")
for sec, sk, n, exp, na, nf in VERIFY:
    print(f"  {sec:9s} {sk}  {n:3d}/{exp:<3d} anchors={na:3d}  interpolated={nf:3d}")
print()
print("section  skupina  parsed/expected")
for sec in SECTIONS:
    for sk in range(1, 7):
        got = [x for x in final if x["section"] == sec and x["skupina"] == sk]
        nums = sorted(x["num"] for x in got)
        miss = sorted(set(range(1, PER[sec] + 1)) - set(nums))
        print(f"  {sec:9s} {sk}   {len(got):3d}/{PER[sec]}   missing={miss if len(miss)<12 else str(len(miss))+' items'}")
print(f"\ntotal {len(final)}   colliding ids: {sum(1 for v in ids.values() if v > 1)}")
json.dump(final, open(OUT / "book_parsed2.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
