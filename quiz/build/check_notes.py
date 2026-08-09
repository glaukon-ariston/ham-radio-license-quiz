"""Verify the expanded note files before they are merged into the quiz.

Checks the things the handoff says must not break:
  * every id in a packet has a note, and no note names an id that does not exist
  * flags from the currency audit survive the rewrite  (rule 4)
  * cite.src is a real source key, and RK/PZM printed pages actually exist  (rules 3, 5)
  * links are well-formed and unique per question         (rule 2)
  * the note is genuinely expanded, not the terse original copied over
  * the answer was not touched                            (rule 1)

    python check_notes.py            # every notes_zzz_expanded_*.json
    python check_notes.py teh1_teorija ...
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE / "work"
SRC = {"NN150/22", "RK", "PZM", "ODLUKA", "OBVEZNI", "TR61-01", "TR61-02", "ERC32",
       "HRS-A", "ZEK"}
MIN_CHARS = 300          # the terse originals sit well under this
PAGE_RE = re.compile(r"(?:tiskana\s+)?str\.\s*(\d{1,3})(?:\s*[–-]\s*(\d{1,3}))?", re.I)

problems, warnings = [], []


def folio_range(book):
    """Printed page numbers that really exist in a book, via booktool's folio map."""
    import booktool
    try:
        _, printed, _ = booktool.load(book)
    except KeyError:
        return None
    return set(printed)


PRINTED = {}


def check(name):
    pkt_path = WORK / f"packet_{name}.json"
    note_path = HERE / f"notes_zzz_expanded_{name}.json"
    if not note_path.exists():
        problems.append(f"{name}: no notes file")
        return 0
    pkt = json.load(open(pkt_path, encoding="utf-8"))["questions"]
    notes = {k: v for k, v in json.load(open(note_path, encoding="utf-8")).items()
             if not k.startswith("_")}

    for qid in pkt:
        if qid not in notes:
            problems.append(f"{name}/{qid}: not covered")
    for qid in notes:
        if qid not in pkt:
            problems.append(f"{name}/{qid}: not in this packet")

    for qid, spec in notes.items():
        p = pkt.get(qid)
        if p is None:
            continue
        note = spec.get("note", "")
        if not note.strip():
            problems.append(f"{name}/{qid}: empty note")
        elif len(note) < MIN_CHARS:
            warnings.append(f"{name}/{qid}: note only {len(note)} chars — expanded enough?")
        if note.strip() == (p["current_explanation"] or "").strip():
            problems.append(f"{name}/{qid}: note unchanged from the terse original")
        if "\n\n" not in note:
            warnings.append(f"{name}/{qid}: single paragraph")
        if "answer" in spec or "options" in spec:
            problems.append(f"{name}/{qid}: notes must not carry an answer or options (rule 1)")

        # rebuild.py never CLEARS a flag, so the flag itself survives an omission — what a
        # rewrite really loses is the warning paragraph in the prose. Check both.
        if p["flag"] and spec.get("flag") != p["flag"]:
            problems.append(f"{name}/{qid}: flag {p['flag']!r} lost or changed "
                            f"-> {spec.get('flag')!r} (rule 4)")
        # Not every flag is legal: prv-057 marks the exam key disagreeing with the Maidenhead
        # standard, which no article of the Pravilnik has an opinion about. Accept either a
        # legal reference or plain divergence language, so a correct note is not rejected for
        # failing to cite a law that does not exist.
        warned = any(w in note.lower() for w in
                     ("⚖", "pravilnik", "zakon", "propis", "čl.", "tablica", "napomena",
                      "provjeriti", "razilaz", "ne slaže", "neslag", "ključ", "iaru"))
        if p["flag"] and not warned:
            problems.append(f"{name}/{qid}: flagged {p['flag']!r} but the new note no longer "
                            f"carries the warning (rule 4)")

        for c in spec.get("cite", []):
            if c.get("src") not in SRC:
                problems.append(f"{name}/{qid}: bad cite src {c.get('src')!r}")
                continue
            if c["src"] in ("RK", "PZM"):
                if c["src"] not in PRINTED:
                    PRINTED[c["src"]] = folio_range(c["src"])
                have = PRINTED[c["src"]]
                for m in PAGE_RE.finditer(c.get("loc", "")):
                    for g in m.groups():
                        if g and have and int(g) not in have:
                            problems.append(f"{name}/{qid}: {c['src']} printed page {g} "
                                            f"does not exist (rule 3/5)")
        if not spec.get("cite"):
            warnings.append(f"{name}/{qid}: no citation")

        urls = [l.get("url", "") for l in spec.get("links", [])]
        for l in spec.get("links", []):
            if not l.get("url", "").startswith("http") or not l.get("label", "").strip():
                problems.append(f"{name}/{qid}: malformed link {l!r}")
            if " " in l.get("url", ""):
                problems.append(f"{name}/{qid}: unescaped space in {l['url']!r}")
        if len(urls) != len(set(urls)):
            problems.append(f"{name}/{qid}: duplicate link in the same question")
        if not urls:
            warnings.append(f"{name}/{qid}: no links")

        for line in spec.get("formula", []):
            if not isinstance(line, str):
                problems.append(f"{name}/{qid}: formula line is not a string")
    return len(notes)


names = sys.argv[1:] or [p.stem.replace("notes_zzz_expanded_", "")
                         for p in sorted(HERE.glob("notes_zzz_expanded_*.json"))
                         if (WORK / f"packet_{p.stem.replace('notes_zzz_expanded_', '')}.json"
                             ).exists()]
total = sum(check(n) for n in names)
print(f"checked {len(names)} batches, {total} notes")
for w in warnings:
    print("  warn ", w)
for p in problems:
    print("  ERROR", p)
print(f"\n{len(problems)} errors, {len(warnings)} warnings")
sys.exit(1 if problems else 0)
