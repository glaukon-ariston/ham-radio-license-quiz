"""Rebuild the whole quiz from the source PDFs in one step.

    parse2.py      HRS banks -> bank.json          (red-text answer key)
    parse_book2.py priručnik -> book_parsed2.json  (coordinate parse + key tables)
    figures2.py    vector figures -> figs/
    this script    assemble questions.json, attach notes, then build_quiz.py
"""
import base64, datetime, glob, json, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
DST = Path(r"g:/My Drive/Electronics/HAM Radio License/quiz")

SOURCES = {
 "NN150/22": {"title": "Pravilnik o amaterskim radijskim komunikacijama, NN 150/2022",
   "file": "docs/Pravilnik_o_amaterskim_radijskim_komunikacijama_NN_150_22.pdf",
   "url": "https://narodne-novine.nn.hr/clanci/sluzbeni/2022_12_150_2313.html"},
 "RK": {"title": "Radiokomunikacije — priručnik HRS (~2005)", "file": "docs/Radiokomunikacije.pdf",
   "note": "Citira se TISKANI broj stranice."},
 "PZM": {"title": "B. Pašarić: Radioamaterizam za mlade", "file": "docs/Pasaric_Radioamaterizam_za_mlade.pdf",
   "note": "Citira se TISKANI broj stranice."},
 "ODLUKA": {"title": "Odluka o provođenju radioamaterskih ispita (HRS)",
   "file": "docs/RA_ispiti_1_Odluka_o_provodjenju_ispita.pdf"},
 "OBVEZNI": {"title": "Obvezni dio ispitnog programa", "file": "docs/Obvezni_dio_ispitnog_programa.pdf"},
 "TR61-01": {"title": "CEPT Preporuka T/R 61-01", "file": "docs/CEPT_preporuka_TR61_01.pdf"},
 "TR61-02": {"title": "CEPT Preporuka T/R 61-02 (HAREC)", "file": "docs/CEPT_Preporuka_TR61_02.pdf"},
 "ERC32": {"title": "ERC Report 32", "file": "docs/ERCRep32.pdf"},
 "HRS-A": {"title": "HRS ispitne liste za A razred (točni odgovori označeni crvenom bojom)",
   "file": "docs/RA_ispiti_7/8/9_A_razred_*.pdf"},
 "ZEK": {"title": "Zakon o elektroničkim komunikacijama, NN 76/2022",
   # ...1113 is a different act in the same issue and returns only NN boilerplate; the Zakon
   # itself is 1116. Checked by fetching both: 1113 is 13 KB with no article text, 1116 is
   # 773 KB and titled "Zakon o elektroničkim komunikacijama".
   "url": "https://narodne-novine.nn.hr/clanci/sluzbeni/2022_07_76_1116.html",
   "note": "Ovlasti nadzora i kazne NISU u Pravilniku NN 150/22 — one su u ZEK-u, na temelju "
           "kojega je Pravilnik i donesen (čl. 16. st. 1. t. 1. i čl. 69. st. 22.)."},
}
FILE = {"tehnicki": "RA_ispiti_9_A_razred_Tehnicki_dio.pdf",
        "propisi": "RA_ispiti_8_A_razred_HR_i_medjunarodni_propisi.pdf",
        "pravila": "RA_ispiti_7_A_razred_Pravila_i_postupci.pdf"}
ROM = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}


def run(script):
    print(f"--- {script}")
    r = subprocess.run([sys.executable, script], cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stdout, r.stderr)
        sys.exit(f"{script} failed")
    print("   " + (r.stdout.strip().splitlines() or ["ok"])[-1])


for s in ("parse2.py", "parse_book2.py", "figures2.py", "book_figures.py"):
    run(s)

hrs = json.load(open(HERE / "bank.json", encoding="utf-8"))
book = json.load(open(HERE / "book_parsed2.json", encoding="utf-8"))
figs = json.load(open(HERE / "figs_index.json", encoding="utf-8"))
bfigs = json.load(open(HERE / "figs_book_index.json", encoding="utf-8"))

for q in hrs:
    q["src"] = "hrs"
    q["status"] = "live"
    q["cite_self"] = {"src": "HRS-A",
                      "loc": f"{FILE[q['section']]}, pitanje {q['number']}, str. {q.get('page','?')}"}
    f = figs.get(q["id"])
    if f:
        data = base64.b64encode((HERE / "figs" / f["file"]).read_bytes()).decode()
        q["figure"] = {"data": f"data:image/png;base64,{data}", "w": f["w"], "h": f["h"]}
        q["figure_is_options"] = bool(q.pop("figure_options", False))
    q.pop("figure_options", None)
    q.pop("red_marks", None)

extra = [{
    "id": b["id"], "section": b["section"], "subsection": None, "number": b["num"],
    "question": b["question"], "options": b["options"], "answer": b["answer"],
    "answer_source": "book-key-table", "src": "book", "status": "live-extra",
    "skupina": b["skupina"], "num_source": b["num_source"],
    "cite_self": {"src": "RK", "loc": f"Ispitna pitanja, SKUPINA {ROM[b['skupina']]}, "
                                     f"pitanje {b['num']}, tiskana str. {b['page']+5}"
                                     + ("" if b["num_source"] == "ocr anchor"
                                        else " (broj pitanja rekonstruiran)")},
    "cite": [{"src": "RK", "loc": f"tablica ODGOVORI NA PITANJA, redak {b['num']}, "
                                  f"stupac Skupina {ROM[b['skupina']]}"}],
} for b in book]

# Six book questions answer with a picture rather than words; carry their crop through.
for e in extra:
    f = bfigs.get(e["id"])
    if f:
        data = base64.b64encode((HERE / "figs_book" / f["file"]).read_bytes()).decode()
        e["figure"] = {"data": f"data:image/png;base64,{data}", "w": f["w"], "h": f["h"]}
        e["figure_is_options"] = f["is_options"]

# attach explanations
byid = {q["id"]: q for q in hrs}
unknown = []
for f in sorted(glob.glob(str(HERE / "notes_*.json"))):
    for qid, spec in json.load(open(f, encoding="utf-8")).items():
        if qid.startswith("_"):
            continue
        q = byid.get(qid)
        if not q:
            unknown.append(qid)
            continue
        q["explanation"] = spec["note"]
        q["cite"] = spec.get("cite", q.get("cite", []))
        for extra_key in ("formula", "links"):
            if spec.get(extra_key):
                q[extra_key] = spec[extra_key]
        # A later file may expand a note without repeating the flag an earlier one set.
        # Flags mark real legal conflicts, so they must survive being rewritten.
        if spec.get("flag"):
            q["flag"] = spec["flag"]
if unknown:
    print("  ! notes for unknown ids:", unknown)

# Fail the build rather than ship a question that cannot be answered. teh-074's options were
# once a) and c) only while its correct answer was b), which no amount of studying could fix.
problems = [f"{q['id']}: answer {q['answer']!r} not among {sorted(q['options'])}"
            for q in hrs + extra if q["answer"] not in q["options"]]
problems += [f"{q['id']}: {len(q['options'])} options" for q in hrs + extra
             if len(q["options"]) != 4]
problems += [f"{q['id']}: empty stem" for q in hrs + extra if not q["question"].strip()]
seen = Counter(q["id"] for q in hrs + extra)
problems += [f"{qid}: duplicated {n}x" for qid, n in seen.items() if n > 1]
if problems:
    sys.exit("BUILD ABORTED — unanswerable questions:\n  " + "\n  ".join(problems[:20]))
print(f"--- integrity ok: {len(hrs) + len(extra)} questions, all answerable")

doc = {"_meta": {}, "_sources": SOURCES, "questions": hrs, "questions_extra": extra}
tot = Counter(q["section"] for q in hrs)
exp = Counter(q["section"] for q in hrs if q.get("explanation"))
doc["_meta"] = {
    "generated": datetime.date.today().isoformat(),
    "live_total": len(hrs), "extra_total": len(extra), "figures": len(figs),
    "explained": sum(1 for q in hrs if q.get("explanation")),
    "explained_by_section": {s: f"{exp[s]}/{tot[s]}" for s in tot},
    "flagged": [(q["id"], q["flag"]) for q in hrs if q.get("flag")],
    "answer_key": "HRS's own red-text marking, extracted from the source PDFs.",
    "exam": {"tehnicki": {"q": 40, "min": 45}, "propisi": {"q": 20, "min": 30},
             "pravila": {"q": 20, "min": 30}, "pass_pct_per_section": 70},
}
DST.mkdir(exist_ok=True)
(DST / "questions.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"--- questions.json  hrs={len(hrs)} extra={len(extra)} "
      f"explained={doc['_meta']['explained']} figures={len(figs)}")
run("build_quiz.py")
print("\ncoverage:", doc["_meta"]["explained_by_section"])
print("flagged :", doc["_meta"]["flagged"])
