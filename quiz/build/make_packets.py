"""Cut the remaining questions into per-topic (HRS) or per-skupina (book) work packets.

A question counts as DONE when it carries `links` — that is the marker of the expanded
style, since every question already had a terse explanation before this pass began.

    python make_packets.py            the 456 HRS questions, cut by topic, as before
    python make_packets.py --book     the 720 priručnik questions, cut by skupina x section
    python make_packets.py --book DIR write the book packets somewhere other than work/

The book cut is by skupina, not by topic, because a skupina is one printed mock exam paper
and that is the unit the priručnik and its answer key are organised in: `bk-teh-<skupina>-NN`
share one printed answer-key column and one contiguous page range, so grouping by skupina
keeps a notes worker's citations on one or two printed pages instead of scattered across six
exams. Each skupina x section is its own packet (tehnički split in half, 30 questions apiece,
since 60 is too many for one item); pravila and propisi are 40 and 20 respectively, small
enough to stay whole. That is 6 skupina x (2 + 1 + 1) = 24 files for 6 x 120 = 720 questions.
"""
import json, sys
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).parent
BOOK = "--book" in sys.argv
rest = [a for a in sys.argv[1:] if not a.startswith("-")]
OUT = Path(rest[0]) if BOOK and rest else HERE / "work"
Q = json.load(open(HERE.parent / "questions.json", encoding="utf-8"))
flagged = dict(Q["_meta"]["flagged"])
POOL = Q["questions_extra"] if BOOK else Q["questions"]
PREFIX = "book_" if BOOK else ""

# (packet name, predicate) — 3. Krugovi, propisi and pravila are split, they are too big for one.
# The subsection test is None-safe: propisi and pravila carry no subsection at all, and one
# book question is deliberately left unclassified rather than guessed.
def teh(n):
    return lambda q: (q["section"] == "tehnicki" and q["subsection"] is not None
                      and q["subsection"].startswith(f"{n}."))


def half(pred, which):
    def f(q, _seen=[]):
        return pred(q)
    return f


PACKETS = [
    ("teh1_teorija", teh(1)),
    ("teh2_komponente", teh(2)),
    ("teh3_krugovi_a", teh(3)),
    ("teh3_krugovi_b", teh(3)),
    ("teh4_prijamnici", teh(4)),
    ("teh5_odasiljaci", teh(5)),
    ("teh6_antene", teh(6)),
    ("teh7_rasprostiranje", teh(7)),
    ("teh8_mjerenja", teh(8)),
    ("teh9_smetnje", teh(9)),
    ("teh10_sigurnost", teh(10)),
    ("propisi_a", lambda q: q["section"] == "propisi"),
    ("propisi_b", lambda q: q["section"] == "propisi"),
    ("pravila_a", lambda q: q["section"] == "pravila"),
    ("pravila_b", lambda q: q["section"] == "pravila"),
]
SPLIT = {"teh3_krugovi": 2, "propisi": 2, "pravila": 2}


def make_body(pool):
    body = OrderedDict()
    for q in pool:
        body[q["id"]] = {
            "number": q["number"],
            "subsection": q["subsection"],
            "question": q["question"],
            "options": q["options"],
            "answer": q["answer"],
            "answer_text": q["options"][q["answer"]],
            "has_figure": bool(q.get("figure")),
            "current_explanation": q.get("explanation", ""),
            "current_cite": q.get("cite", []),
            "current_formula": q.get("formula"),
            "flag": flagged.get(q["id"]),
            "hrs_source": q["cite_self"]["loc"],
        }
    return body


def write_packet(name, pool):
    body = make_body(pool)
    p = OUT / f"packet_{PREFIX}{name}.json"
    p.write_text(json.dumps({"_packet": name, "_count": len(body), "questions": body},
                            ensure_ascii=False, indent=1), encoding="utf-8")
    n_flagged = sum(1 for q in pool if flagged.get(q["id"]))
    print(f"  {name:24s} {len(body):3d} questions  ({n_flagged} flagged)")


OUT.mkdir(parents=True, exist_ok=True)
todo = [q for q in POOL if not q.get("links")]
print(f"{len(todo)} of {len(POOL)} still to expand")

assigned = set()
if BOOK:
    # One packet per skupina x section (18 groups); tehnicki is additionally split in
    # half because 60 questions is too many for one item. The split interleaves on
    # printed question number so each half still spans the whole exam paper, not just
    # its first or second thirty.
    for skupina in range(1, 7):
        for section in ("tehnicki", "propisi", "pravila"):
            pool = sorted((q for q in todo
                           if q["skupina"] == skupina and q["section"] == section),
                          key=lambda q: q["number"])
            pool = [q for q in pool if q["id"] not in assigned]
            if section == "tehnicki":
                halves = [(pool[0::2], "_a"), (pool[1::2], "_b")]
            else:
                halves = [(pool, "")]
            for half, suffix in halves:
                if not half:
                    continue
                assigned.update(q["id"] for q in half)
                write_packet(f"s{skupina}_{section}{suffix}", half)
else:
    for name, pred in PACKETS:
        base = name.rsplit("_", 1)[0] if name[-2:] in ("_a", "_b") else name
        pool = [q for q in todo if pred(q)]
        if base in SPLIT:
            n = SPLIT[base]
            part = 0 if name.endswith("_a") else 1
            pool = pool[part::n]          # interleave, so each half spans the whole topic
        pool = [q for q in pool if q["id"] not in assigned]
        assigned.update(q["id"] for q in pool)
        if not pool:
            continue
        write_packet(name, pool)

missing = [q["id"] for q in todo if q["id"] not in assigned]
if missing:
    print("  ! unassigned:", missing)
print(f"total assigned: {len(assigned)}")
