# HAM Radio A-class exam quiz (Croatia)

A practice quiz for the Croatian amateur radio **A-class (napredni razred)** licence exam,
built from the Hrvatski radioamaterski savez's (HRS) own answer-marked exam banks. **1176
questions**, every one carrying a cited teaching note.

**Try it:** _(link goes live once GitHub Pages is set up — see P2-0058)_

---

## How it's built

HRS's exam PDFs mark every correct answer in **red text**. That's invisible to `pdftotext`
and to every other text extractor — almost certainly why no answer key circulates online.
Reading the PDFs with [PyMuPDF](https://pymupdf.readthedocs.io/) instead recovers the colour
*and* fixes the encoding, since `pdftotext` also mangles Croatian diacritics (`č ć ž š đ`).

The result: all **456** official HRS questions carry HRS's own authoritative answer — not a
derived one. Those are cross-validated against the 2005 HRS priručnik
(`Radiokomunikacije.pdf`), which has its own independent answer-key tables; on strictly
matched question pairs the two sources currently agree on **96.3%** (104/108). Every
disagreement is a genuine change between the 2005 book and today's material, not a
mis-alignment — see `quiz/REVIEW.md`. The priručnik also supplies **720** additional
practice-only questions (not exam-eligible), for **1176** total.

Every one of the 1176 questions carries a teaching note: a worked derivation for numeric
questions, an article citation for regulatory ones — sourced, never invented.

The whole corpus rebuilds from the source PDFs in one command:

```
python quiz/build/rebuild.py
```

See `QUIZ_PLAN.md` for the full method, including the parser quirks (two-column option
layout, symbol-font glyphs, relettered options) and the two hazards documented there: the
book is legally out of date on regulatory matters, and answer *letters* can't be copied
across sources — only option *text* can.

---

## Sources & acknowledgments

None of the source PDFs are redistributed in this repository (see below) — this section
credits them and tells you how to get your own copy.

### Public regulatory / institutional texts

| Document | Source |
|---|---|
| Pravilnik o amaterskim radijskim komunikacijama (NN 150/22) | [narodne-novine.nn.hr](https://narodne-novine.nn.hr/clanci/sluzbeni/2022_12_150_2313.html) |
| CEPT Recommendation T/R 61-01 | [hamradio.hr](https://www.hamradio.hr/download/CEPT_preporuka_TR61_01.pdf) |
| CEPT Recommendation T/R 61-02 (HAREC syllabus) | [hamradio.hr](https://www.hamradio.hr/download/CEPT_Preporuka_TR61_02.pdf) |
| ERC Report 32 | [hamradio.hr](https://www.hamradio.hr/download/ERCRep32.pdf) |
| Odluka o provođenju ispita | [hamradio.hr](http://www.hamradio.hr/download/RA_ispiti_1_Odluka_o_provodjenju_ispita.pdf) |
| Odluka o imenovanju povjerenstva | [hamradio.hr](http://www.hamradio.hr/download/RA_ispiti_2_Odluka_o_imenovanju_povjerenstva.pdf) |
| Rješenje o iznosu naknada | [hamradio.hr](http://www.hamradio.hr/download/RA_ispiti_3_Rjesenje_o_iznosu_naknada.pdf) |
| Obavezni dio ispita | [hamradio.hr](http://www.hamradio.hr/download/RA_ispiti_4_Obavezni_dio_ispita.pdf) |
| HAKOM — dopunsko rješenje o imenovanju povjerenstva za P razred | [hamradio.hr](https://www.hamradio.hr/download/HAKOM_Dopunsko_rjesenje_P_razred.pdf) |

Every link above was fetched this session and confirmed to serve the same document as this
project's local copy (matching byte size, and matching title/content where the PDF has a
text layer). The CEPT/ERC documents originate with CEPT/ECC; they're linked here via HRS's
own download page (`hamradio.hr`) because that's HRS's own published source for exam
candidates, and because CEPT's own document database (`docdb.cept.org`) could not be reached
over a trusted connection at the time of writing (TLS certificate could not be verified).

### HRS's own exam & instructional material

- **The three A-class question banks** — `RA_ispiti_7_A_razred_Pravila_i_postupci.pdf`,
  `RA_ispiti_8_A_razred_HR_i_medjunarodni_propisi.pdf`,
  `RA_ispiti_9_A_razred_Tehnicki_dio.pdf` — and the corresponding three P-class banks
  (`RA_ispiti_10/11/12`). Published by HRS.
- **`Radiokomunikacije.pdf`** (`_ocr.pdf`) — HRS's 410-page official priručnik, ~2005.
  Rendering its own introduction page confirms it is authored by **Mladen Zadro, dipl. ing.**
  (voditelj/lead author), with co-authors **Ante Botica, dipl. ing.**, **dr. sc. Draško
  Marin**, and **Vladimir Štancl, ing.**, reviewed by **dr. sc. Zvonimir Jakobović** and
  **mr. sc. Željko Ulip**, and published by Hrvatski radioamaterski savez.
- **`ZBIRKA-1_Prirucnik-Radiokomunikacije-2023.pdf`** — despite its filename this is a
  *different* work: "Priručnik praktičnih radova za pripremu natjecanja mladih tehničara u
  području radiokomunikacije" (2023), authored by **Jelena Tuksar, mag. ing.**, **mr. sc.
  Željko Ulip**, and **Stipe Predanić, dipl. ing.**, published by HRS — confirmed from its
  own title page.

### One externally-authored, out-of-print book

`Pasaric_Radioamaterizam_za_mlade.pdf` — *"Radioamaterizam za mlade — priručnik za polaganje
operatorskog P-ispita"*, by **Božidar Pasarić, 9A2HL**, Zagreb 2008, published in the
University of Zagreb's official textbook series ("Udžbenici Sveučilišta u Zagrebu" /
*Manualia Universitatis Studiorum Zagrabiensis*) — confirmed from the book's own title and
colophon pages. Publisher of record: Hrvatski radioamaterski savez.

---

## The self-improving system

**What's real today:** content work on this project runs through a small internal pipeline —
`queue/` holds one work item per file (`queue/QUEUE.md` is the contract), drained by the
`/drain` skill using worker and checker subagents so each change is independently reviewed
before landing. Two build-time guards backstop it: `rebuild.py` aborts rather than ship a
question with no valid answer, the wrong option count, an empty stem, or a duplicate id, and
`strict.py` re-runs the book-vs-HRS cross-check on every rebuild so an edit that breaks
agreement is caught immediately, not discovered by a test-taker.

**What's not built yet:** there is no in-quiz feedback UI, and no automated path from a
reader spotting a problem to a queue item being filed. `quiz/quiz.html` has no
feedback-submission code today — if you find a mistake, please open a GitHub issue. Turning
that into a closed loop is on the roadmap, not shipped.

---

## License

- **Code** (the Python build pipeline under `quiz/build/`, and the generated quiz
  HTML/JS) — **MIT**.
- **Teaching notes and citations** (the content of `quiz/build/notes_*.json`) — these are
  Glaukon's own authored derivative work, and are **CC BY-SA**.
- **The underlying exam questions and answer keys** are HRS's own material, used here under
  citation. They are covered by neither license grant above; this project does not claim to
  license HRS's content, only its own code and notes.

No `LICENSE` file has been added yet — this section states intent; formal SPDX license files
may follow in a separate change.

---

## Origin story

This project grew out of one person's own preparation for the A-class exam. The full
background — including the pico-balloon project it was originally undertaken for — is in
[`PLAN.md`](PLAN.md); the quiz-specific plan, method, and status are in
[`QUIZ_PLAN.md`](QUIZ_PLAN.md).

---

## Disclaimer

This is an unofficial, independent project. It is not affiliated with, endorsed by, or
produced by Hrvatski radioamaterski savez (HRS) or HAKOM. Answer accuracy is tied to HRS's
own published exam key at the time each source PDF was captured; always check current HRS
material before an exam.
