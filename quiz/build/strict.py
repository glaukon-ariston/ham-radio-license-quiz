"""Strict cross-validation: compare answers ONLY on pairs that are certainly the same
question, i.e. the stems match AND the four options match as a SET.

The loose matcher pairs generic stems ("Filtar na slici je:") with the wrong HRS
question, which shows up as a fake disagreement. Requiring the option set to coincide
removes that whole class: if both questions offer the same four choices, they are the
same question, and a differing answer is then either a real numbering error or a real
key difference.
"""
import json, difflib, re, unicodedata, sys
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).parent

def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.replace("đ", "d").replace("ð", "d"))

def sim(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

hrs = json.load(open(OUT / "bank.json", encoding="utf-8"))
book = json.load(open(OUT / "book_parsed2.json", encoding="utf-8"))
for h in hrs:
    h["norm"] = norm(h["question"])
    h["onorm"] = {k: norm(v) for k, v in h["options"].items()}
by_sec = {}
for h in hrs:
    by_sec.setdefault(h["section"], []).append(h)

def digits(s):
    return re.findall(r"\d+", s)


# Emission/mode abbreviations that change a question's MEANING, not its spelling. Deliberately
# a short curated list rather than "any ALL-CAPS token": a blanket abbreviation-set comparison
# also flags 'IARU' against the book OCR's 'LARU' (an I/L glyph misread, same question,
# bk-pra-2-18 vs prv-004 — one of the documented OCR error classes in REVIEW.md) as a
# mismatch, which would silently drop a correct agreement. Restricting to modes avoids that:
# an OCR misread never happens to land on a *different* real mode abbreviation.
MODES = {"USB", "LSB", "SSB", "CW", "AM", "FM", "FSK", "RTTY", "PSK", "PSK31", "AFSK",
         "SSTV", "FAX", "DSB", "A1A", "A3E", "F1B", "F3E", "J3E"}


def modes(s):
    """Mode/emission tokens actually present in a RAW (un-normalised) stem. A templated stem
    that differs only in its mode word is a DIFFERENT question, not a matching one —
    'Na kojim KV frekvencijskim podrucjima se koristi LSB modulacija?' and the same sentence
    with USB score 0.9+ on plain similarity (one three-letter run out of ~60 chars) and offer
    the identical four band options, so the old matcher paired them as the same question and
    reported a fake key disagreement (prv-009 vs bk-pra-5-05). Both keys are correct for their
    own, different, question."""
    return set(re.findall(r"[A-Z][A-Z0-9]{1,5}", s)) & MODES


def same(a, b):
    """Two option texts are the same option. Short numeric answers need care: '10 W' and
    '100 W' score 0.857 on plain similarity, which silently paired a 2005 question with its
    modern replacement and reported it as a key disagreement. Require the digits to match."""
    if digits(a) != digits(b):
        return False
    return sim(a, b) >= 0.85


def setmatch(bo, ho):
    """Greedy 1-1 pairing of the four options; returns the mapping if all four match."""
    pool = dict(ho)
    out = {}
    for k, v in bo.items():
        if not pool:
            return None
        j = max(pool, key=lambda j: sim(v, pool[j]))
        if not same(v, pool[j]):
            return None
        out[k] = j
        del pool[j]
    return out

tally, bad = Counter(), []
for b in book:
    bo = {k: norm(v) for k, v in b["options"].items()}
    for h in by_sec.get(b["section"], []):
        if sim(b["norm"], h["norm"]) < 0.90:
            continue
        if modes(b["question"]) != modes(h["question"]):
            continue
        m = setmatch(bo, h["onorm"])
        if not m:
            continue
        src = b.get("num_source", "?")
        ok = m.get(b["answer"]) == h["answer"]
        tally[f"{src} {'AGREE' if ok else 'DISAGREE'}"] += 1
        if not ok:
            bad.append((src, b["id"], h["id"], h["question"][:75],
                        h["options"][h["answer"]][:65], b["options"][b["answer"]][:65]))
        break

print("=== strict validation (same stem AND same option set) ===")
tot_a = tot_d = 0
for src in ("ocr anchor", "interpolated (gap arithmetically forced)"):
    a, d = tally[src + " AGREE"], tally[src + " DISAGREE"]
    tot_a, tot_d = tot_a + a, tot_d + d
    if a + d:
        print(f"  {src:45s} {a}/{a+d} = {100*a/(a+d):.1f}%")
print(f"  {'TOTAL':45s} {tot_a}/{tot_a+tot_d} = {100*tot_a/(tot_a+tot_d):.1f}%")
print(f"\n--- {len(bad)} disagreements ---")
for src, bid, hid, q, ha, ba in bad:
    print(f"\n{hid} <- {bid}   [{src}]")
    print(f"  Q   : {q}")
    print(f"  HRS : {ha}")
    print(f"  book: {ba}")
