"""Cut the remaining questions into per-topic work packets.

A question counts as DONE when it carries `links` — that is the marker of the expanded
style, since every question already had a terse explanation before this pass began.

    python make_packets.py            the 456 HRS questions, as before
    python make_packets.py --book     the 720 priručnik questions, same topic cut
    python make_packets.py --book DIR write the book packets somewhere other than work/

The book cut exists because a skupina is a whole mock exam: its 60 technical questions span
theory, components, circuits and antennas at once, so grouping by skupina makes every notes
item load reference material for all ten topics. Book questions get their topic from
book_subsections.json (see rebuild.py); the propisi and pravila ones have none, because the
HRS banks for those sections carry no chapter headings either, and they fall out by section.
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

OUT.mkdir(parents=True, exist_ok=True)
todo = [q for q in POOL if not q.get("links")]
print(f"{len(todo)} of {len(POOL)} still to expand")

assigned = set()
index = []
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
    p = OUT / f"packet_{PREFIX}{name}.json"
    p.write_text(json.dumps({"_packet": name, "_count": len(body), "questions": body},
                            ensure_ascii=False, indent=1), encoding="utf-8")
    index.append((name, len(body), sum(1 for q in pool if flagged.get(q["id"]))))
    print(f"  {name:24s} {len(body):3d} questions"
          f"  ({sum(1 for q in pool if flagged.get(q['id']))} flagged)")

missing = [q["id"] for q in todo if q["id"] not in assigned]
if missing:
    print("  ! unassigned:", missing)
print(f"total assigned: {len(assigned)}")
