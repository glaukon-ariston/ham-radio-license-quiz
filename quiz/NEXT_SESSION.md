# Handoff — the expansion pass is DONE

Written 9 August 2026. The task Glaukon set on 9 August — longer, less terse explanations on
**every** question, with worked maths, external links and a reference to the local books — is
**complete: 456 of 456**. This file now records what was done, what a rebuild must not undo,
and what is genuinely left.

---

## State

| | |
| --- | --- |
| Expanded notes | **456 / 456** (450 carry a worked `formula` block) |
| External links | 293 distinct, all fetched, none a disambiguation page |
| Figures | **52** (was 46 — six were never even attempted, see below) |
| Flags | 33 (was 32 — `teh-192` is new) |
| `strict.py` | **103/108 = 95.4 %** (was 102/107) |
| Artifact | published, same URL, favicon 📻 |

Everything is rebuilt from source in one step:

```bash
python quiz/build/rebuild.py     # ABORTS on an unanswerable question
python quiz/build/check_notes.py # coverage, flags, citations, links
python quiz/build/link_check.py  # fetches every link; fails on disambiguation pages
python quiz/build/strict.py      # book-vs-HRS cross-check, expect 102/107
```

## Three answers were WRONG and are now fixed — do not retype them

The four diagram-answer questions have their answers **typed in by hand** in
`build/overrides.json`, and three of the original four were typed wrong. Verified against the
red span in the HRS PDF:

| id | was | HRS marks |
| --- | --- | --- |
| `teh-075` | `c` | **`d`** |
| `teh-095` | `a` | **`b`** |
| `teh-114` | `a` | **`c`** |
| `teh-074` | `b` | `b` ✓ |

`teh-114` is corroborated three ways (red span, the figure, and RK 5.4.10 — *"Kada imamo 100
posto modulaciju trapez će prijeći u trokut"*). **If a future pass "restores" these from the old
values it silently reintroduces three wrong answers.** To re-check all four: list the coloured
spans falling between a question's stem and the next question's stem.

## Figures are found by measuring ink, not by reading the stem

`figures2.py` used to attempt a crop only when the stem said "slika"/"shema"/"crtež". Six
questions show a drawing and never say so — `teh-024`, `teh-041`, `teh-042`, `teh-046`,
`teh-112`, `teh-277` — and all six went to Glaukon pictureless. A question now also earns a
figure from `nontext_ink()`: render the band below its options, paint every **character**
white, count what is left. Text-only questions score exactly **0**; the six score 1019–3300.

Three things about that function are load-bearing, and each was a bug first:

- Mask **characters**, not lines or spans. Figure labels sit on baselines padded with leading
  spaces whose bbox covers the drawing — a span-level mask reported `teh-112`'s spectrum as
  blank paper.
- Measure the band **below the options only**. `teh-017` and `teh-081` hold a formula image
  inside the *stem*, already transcribed in `overrides.json`; a whole-question measurement
  re-ships the question as a picture of itself.
- Choose between the two candidate bands by **drawing** ink, never total ink. Total ink always
  favours the whole-question band, which is how `teh-277` came to display its own options with
  the marked one still legible by its typeface.

## The tooling you now have

- **`build/booktool.py`** — resolves printed page numbers. `Radiokomunikacije.pdf` is a **pure
  scan with no text layer**; the searchable twin is `Radiokomunikacije_ocr.pdf`, page-for-page
  identical, and booktool uses it automatically.
  `map` / `find` / `page` / `toc`; `page RK pdf199` takes a raw index.
  RK resolves in four regions (0-based): pdf 0–9 `+3`, 10–280 `+4`, 281–350 `+6`, 351–409 `+7`.
  PZM is a clean `+1` throughout.
- **`build/check_notes.py`** — the merge gate. Run it before believing any batch.
- **`build/link_check.py`** — fetches every link **and** rejects Wikipedia disambiguation
  pages via the API's pageprops. Scraping the HTML for "disambiguation" does NOT work; it
  false-positives on ordinary articles.
- **`build/make_packets.py`** + **`build/work/`** — per-topic packets, `BRIEF.md`, `LEGAL.md`,
  `LINKS.md`. Regenerate packets only if you start another pass.

## Traps that cost time this session

1. **`quiz/build/currency_findings.json` does not exist.** The old handoff and the memory file
   both point at it. The audit's surviving record is `notes_zz_currency.json` plus each
   question's prose. Do not promise a future session that file.
2. **OCR writes numbers with spaces.** Grepping RK for `21151` finds nothing; the page says
   `21 151`. A number can look absent when it is right there.
3. **Wikipedia disambiguation pages return HTTP 200.** Six Croatian titles I had "verified"
   were disambiguations; 22 links shipped before it was caught. `LINKS.md` lists them with
   replacements.
4. **The ZEK link was wrong everywhere** — `...2022_07_76_1113.html` is a different act and
   serves only boilerplate. The Zakon is **`..._1116.html`**. Fixed in `rebuild.py`, `LINKS.md`
   and 9 notes.
5. **`rebuild.py` never clears a flag**, it only sets one — so a flag survives a rewrite that
   omits it. What a rewrite really loses is the warning paragraph in the prose. `check_notes.py`
   checks both.
6. **`get_images()` and `get_drawings()` both return empty on pages that plainly show a
   circuit.** These PDFs are PrimoPDF output: the line art is ~950 one-pixel INLINE images per
   page, which `get_images()` does not report and `get_drawings()` cannot see as paths. That
   false negative is what made an earlier session declare `teh-024`'s diagram "missing from the
   source". **Render the page and look at it before concluding anything is absent.**

## What is genuinely left

Nothing is required. In rough order of value:

1. **Two questions where the club should adjudicate** — `prv-057` (locator: the key says 10°
   longitude × 20° latitude; Maidenhead is the reverse, and 18 × 20° = 360° proves it) and
   `teh-261` (HRS marks "replace the TV antenna cable", RK's own table marks "fit a mains
   filter"; outside `strict.py`'s verified mapping).
2. **`teh-103` is the one question with no citation.** Deliberate: neither book states the
   Shannon–Hartley theorem, and rule 5 says cite nothing rather than something plausible.
3. **Notes for the 720 `questions_extra` book questions.** They are answerable and cited to the
   book's key table, but carry no teaching notes. That is the only large body of work left.
4. The five `strict.py` disagreements (`teh-201`, `teh-273`, `pro-090`, `pro-047`, `prv-009`)
   are documented in REVIEW.md §2–4 and unchanged.

## Rules that still must not be broken

1. **Never change the HRS answer** on the basis of your own physics. Correcting a
   *transcription* of the key (above) is a different thing and is fine — but verify against the
   red span first.
2. **Every external link fetched and confirmed**, and not a disambiguation page.
3. **Verify every printed page against the page itself.** Use `booktool.py`.
4. **Preserve flags and the warning prose that goes with them.**
5. **Do not invent an article number or a page.** Say so in the note and cite nothing.
6. **PyMuPDF, never `pdftotext`** (it destroys Croatian diacritics), and set
   `PYTHONIOENCODING=utf-8` before any Python that prints Croatian to a console.

## Publishing

The quiz is **one artifact that already exists**:

> <https://claude.ai/code/artifact/6b181da6-b6a3-4486-8329-d4e5dc1ad346>

Pass that as `url:` or a new conversation mints a new link and Glaukon loses his bookmark. Keep
the favicon 📻 and the title unchanged. `build_quiz.py` already emits artifact-shaped HTML
(a `<title>` plus content, no `<!doctype>`/`<html>`/`<head>`/`<body>`), so publish it directly.

## Background

- `quiz/REVIEW.md` — every human judgement call. **§4 is this session**: the three wrong
  answers, the figure-extractor faults, the citation rot, the book errors.
- `QUIZ_PLAN.md` — sources, the red-key discovery, build order.
