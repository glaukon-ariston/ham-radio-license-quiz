# Plan: A-class exam quiz

**Companion to `PLAN.md`.** That document covers the licence, the club and the balloons.
This one covers building a practice quiz for the A exam.
**Written:** 8 August 2026

Target: a working quiz before the grind phase starts (**14 Sep 2026** per `PLAN.md`).

> **Status: complete, five weeks early.** `quiz/quiz.html` holds **1 176 questions** — all 456
> official HRS questions, every one with a cited explanation, plus all **720** questions of the
> priručnik. Rebuild the whole thing from the source PDFs with `python quiz/build/rebuild.py`.

---

## The problem — and how it dissolved

The original premise was that the HRS banks publish questions without marking the correct
answer, making a derived answer key the whole project. That premise was **wrong**.

**The HRS PDFs mark every correct answer in red text** (`#ff0000` and `#c00000`). `pdftotext`
discards colour, so the key is invisible to every text extraction — which is almost certainly
why no answer key circulates online, and why `hrvhf.net/ispit/online.php` and
`testovi.marp.org.me` don't have one either.

Reading the PDFs with PyMuPDF instead recovers colour **and** fixes the encoding: the
Croatian diacritics `č ć ž š` come through intact where `pdftotext` mangles them.

**Result: 456 of 456 questions carry an authoritative answer** — HRS's own marking, not a
derivation of mine. This removes the two largest tasks from the plan (deriving ~455 answers,
and repairing diacritics) and makes `docs/Radiokomunikacije.pdf` a cross-check and a source
of extra questions rather than the primary key.

> Keep this in mind if the corpus is ever rebuilt: extract with **PyMuPDF**, never `pdftotext`.

`docs/Radiokomunikacije.pdf` remains useful: it is the HRS priručnik, carries its own answer
keys, and holds ~700 questions. But it is a 410-page scan with no text layer, and from ~2005.

**All 720 of them are now in.** Getting there took a parser that reasons about page coordinates
and a numbering rule that refuses to guess — see `quiz/REVIEW.md` for the method, the evidence
that it is right, and the 31 questions that had to be read by eye because no parser could reach
them. The book's independent answer key agrees with the HRS red key on **95.3 %** of strictly
matched questions, and **100 %** of those whose number the OCR read directly; every remaining
difference is a genuine change between the 2005 book and today's material, not a mis-alignment.

---

## Sources

### HRS banks — current, and answer-marked

| Bank | File | Questions |
|---|---|---|
| Tehnički dio | `docs/RA_ispiti_9_A_razred_Tehnicki_dio.pdf` | 282, in 10 sections |
| HR i međunarodni propisi | `docs/RA_ispiti_8_A_razred_HR_i_medjunarodni_propisi.pdf` | 95 |
| Pravila i postupci | `docs/RA_ispiti_7_A_razred_Pravila_i_postupci.pdf` | 79 |

**456 total, all with answers.** These are what clubs actually draw from — Odluka
`docs/RA_ispiti_1_Odluka_o_provodjenju_ispita.pdf` t. 12: clubs *may* choose other questions
but in practice use these lists.

Quirks handled by the parser (`quiz/build/parse2.py`):

- Options are laid out in **two columns**, so a physical line holds `a)` on the left and `c)`
  on the right — reading order is a, c, b, d, not alphabetical.
- Lines are split into fragments that **overlap by a character** (`"…24 GHz"` + `"z. Koliki"`),
  so fragments are joined with de-duplication.
- Technical questions 44 and 47 of `pravila`, and one block in `tehnicki`, are lettered
  **e)–h)** instead of a)–d); these are relabelled, order preserved.
- Symbol-font glyphs (Ω λ μ π Δ) arrive as private-use codepoints and are remapped.
- **Question 186 of the technical bank is followed by an unnumbered question**
  ("Duljina strane quad radijatora i polarizacija su:"). It is kept as `teh-186b`.
- Four technical questions have **diagrams as their options** rather than text.

Every manual correction lives in `quiz/build/overrides.json` with a stated reason, so no
human judgement is buried inside the parser.

### Radiokomunikacije.pdf — has keys, but from 2005

410 scanned pages (1300×1889 JPEG, no text layer). PDF page = printed page − 6.
Exam material is six mock papers per section, each with an answer-key grid at the end:

| Section | Printed pp. | Structure | Key at |
|---|---|---|---|
| A — Tehnički dio | 287–353 | Skupina I–VI × 60 q ≈ **360** | 354–355 |
| B — Propisi | 357–~374 | Skupina I–VI | ~375–376 |
| C — Pravila i postupci | 377–~408 | Skupina I–VI × 40 q ≈ **240** | 409–410 |

Keys are grids of question number × Skupina → A/B/C/D.

Overlap with the HRS banks is high — every question spot-checked so far (IARU abbreviation,
MAYDAY, "čemu je namijenjena radioamaterska postaja") appears verbatim in both, same options,
same order.

---

## Two hazards

### 1. The book is legally out of date

Its bibliography cites *Zakon o telekomunikacijama* NN 122/03 and *Pravilnik* NN 198/03.
**The current Pravilnik is NN 150/22** — a complete rewrite, 17 years later. The book also states
the A exam is sat *"pri Ministarstvu"*, which is no longer true.

Its **technical** answers are timeless and authoritative. Its **regulatory** answers are not
trustworthy without checking.

### 2. Answer letters cannot be copied across mechanically

Where a question appears in both sources the option *order* may differ, so the key's letter can
point at the wrong option in the HRS wording. **Match on option text, never on letter.**

---

## Corpus design

One deduplicated bank. A question present in both sources is a **single** entry carrying both
source tags — not two entries. Otherwise near-duplicates get drilled twice and exam-simulation
sampling skews.

| Tag | Source | Treatment |
|---|---|---|
| `hrs` | HRS bank only | Exam-eligible |
| `hrs+book` | matched in both | Exam-eligible, answer verified against the book's key |
| `book` | book only (~700) | Extra practice; **excluded from exam-sim by default** so simulation stays representative |

### The quarantine rule

Every regulatory question, from either source, is checked against Pravilnik NN 150/22:

- **confirmed** — book key agrees with current law → normal
- **corrected** — law changed; answer updated, *both* old and new recorded, so a club examiner
  working from stale material doesn't blindside you
- **quarantined** — no valid answer under current law (asks about a licence class or issuing body
  that no longer exists). Kept, flagged, off by default.

Every corrected and quarantined item lands in `REVIEW.md` — which is also the right document to
put in front of the club.

---

## Build order

1. ~~**Extract the HRS banks**~~ **DONE** → `quiz/questions.json`, 456 questions, every one
   carrying HRS's own red-marked answer. Built by `quiz/build/parse2.py` + `overrides.json`.
2. ~~**Ingest the book's text version**~~ **DONE** → **720 / 720**, every skupina complete, via
   `parse_book2.py`, which parses by **coordinates** rather than OCR reading order, since the OCR
   emits the number column separately from the text and drops or mangles many numbers. 689 came
   out of the parser; the last 31 were read by eye into `build/book_overrides.json`.
3. ~~**Read the ~8 answer-key pages visually**~~ **DONE** → `quiz/build/book_keys.json`,
   transcribed by eye. Grids of single letters are the one place an OCR slip silently poisons
   dozens of answers, and there were only eight pages.
4. ~~**Match book ↔ HRS on option text**~~ **DONE** — used for cross-validation rather than
   deduplication: the two banks are kept separate so exam simulation can draw only the official
   one. Agreement **102/107 = 95.3 %** on strictly-matched pairs (**100 %** where the number came
   straight from the OCR), all five differences explained in `REVIEW.md`. Re-runnable any time
   with `python quiz/build/strict.py`.
5. **Derive answers for book-only questions** — not needed. The book's own key tables resolve all
   720, so nothing had to be inferred from first principles.
6. **Currency pass** over all regulatory answers per the quarantine rule. This still applies to
   the HRS banks: their red key is authoritative for *the exam*, but the exam material itself
   may lag NN 150/22. Where the two disagree, record both. Band/power questions done; four
   conflicts flagged in the quiz UI.
7. ~~**Crop figures**~~ **DONE** → **51 figures** (45 HRS + 6 book), cropped as vector line art
   rendered from the page (`pdfimages` reports none, which is what made me miss them initially).
   Every crop has its red answer-mark recoloured to black so the picture cannot give the answer
   away — verified 0 leaks across all 51.
8. ~~**Teaching notes**~~ **DONE** for all 456 official questions — worked derivations for numeric
   ones, article numbers for regulatory ones, every one with a citation.
9. ~~**Build the quiz**~~ **DONE** → `quiz/quiz.html`, rebuilt end-to-end by `build/rebuild.py`.

`questions.json` is the single source of truth. Everything generates from it, so one corrected
answer fixes every output at once.

`rebuild.py` **aborts** rather than emit a question whose answer is not among its options, whose
option count is not four, whose stem is empty, or whose id is duplicated. That guard exists
because `teh-074` once shipped offering only a) and c) while its correct answer was b) — a
question no amount of studying could get right.

---

## The quiz

Self-contained HTML artifact — phone-friendly, no install, progress in `localStorage`.

**Exam simulation** mirrors the real thing exactly, per Odluka t. 5, 7 and 9:

| | Questions | Time | Pass |
|---|---|---|---|
| Tehnički sadržaj | 40 | 45 min | 70% |
| Propisi | 20 | 30 min | 70% |
| Pravila i postupci | 20 | 30 min | 70% |

70% **in each** section. Failing one means retaking all three, minimum 2-month gap, €11.

> Several websites still quote an obsolete 120-question format (60/40/20). Ignore them —
> the 40/20/20 structure above is straight from the current Odluka.

Also: topic practice by subsection, shuffled option order (so you can't memorise "always b"),
a wrong-answer drill queue, and per-question teaching notes revealed after answering.

---

## Language

Questions verbatim in Croatian, matching exam wording exactly. Explanations in Croatian.
A-class banks only — `PLAN.md` establishes P is a strict subset.
