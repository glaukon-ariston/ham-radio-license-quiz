# HAM Radio A-class exam quiz (Croatia)

A practice quiz for the Croatian amateur radio **A-class (napredni razred)** licence exam,
built from the Hrvatski radioamaterski savez's (HRS) own answer-marked exam banks. **1176
questions**, every one carrying a cited teaching note.

For the official path to getting licensed — registration, courses, booking the exam itself —
see HRS's own guide: [*Kako postati radioamater?*](https://www.hamradio.hr/kako-postati-radioamater/).
This project only covers exam prep, not the surrounding process.

**Try it:** [glaukon-ariston.github.io/ham-radio-license-quiz](https://glaukon-ariston.github.io/ham-radio-license-quiz/quiz/quiz.html)

---

## How it's built

HRS's exam PDFs mark each question's correct answer in red text. This project reads that
colour straight out of HRS's own exam PDFs to build the answer key.

The result: all **456** official HRS questions carry HRS's own authoritative answer — not a
derived one. Those are cross-validated against the 2005 HRS priručnik
(`Radiokomunikacije.pdf`), which has its own independent answer-key tables; on strictly
matched question pairs the two sources currently agree on **96.3%** (104/108). Every
disagreement is a genuine change between the 2005 book and today's material, not a
mis-alignment — see `quiz/REVIEW.md`. The priručnik also supplies **720** additional
practice-only questions (not exam-eligible), for **1176** total.

Every one of the 1176 questions carries a teaching note: a worked derivation for numeric
questions, an article citation for regulatory ones.

The whole corpus rebuilds from the source PDFs in one command:

```bash
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
| Obavezni dio ispita (byte-identical file, published under two names/URLs) | [hamradio.hr (RA_ispiti_4)](http://www.hamradio.hr/download/RA_ispiti_4_Obavezni_dio_ispita.pdf), [hamradio.hr (ispitni program)](http://www.hamradio.hr/download/Obvezni_dio_ispitnog_programa.pdf) |
| HAKOM — dopunsko rješenje o imenovanju povjerenstva za P razred | [hamradio.hr](https://www.hamradio.hr/download/HAKOM_Dopunsko_rjesenje_P_razred.pdf) |

Every link above was fetched this session and confirmed to serve the same document as this
project's local copy (matching byte size, and matching title/content where the PDF has a
text layer). The CEPT/ERC documents originate with CEPT/ECC; they're linked here via HRS's
own download page (`hamradio.hr`) because that's HRS's own published source for exam
candidates, and because CEPT's own document database (`docdb.cept.org`) could not be reached
over a trusted connection at the time of writing (TLS certificate could not be verified).

### HRS's own exam & instructional material

- **The three A-class question banks** —
  [`RA_ispiti_7_A_razred_Pravila_i_postupci.pdf`](http://www.hamradio.hr/download/RA_ispiti_7_A_razred_Pravila_i_postupci.pdf),
  [`RA_ispiti_8_A_razred_HR_i_medjunarodni_propisi.pdf`](http://www.hamradio.hr/download/RA_ispiti_8_A_razred_HR_i_medjunarodni_propisi.pdf),
  [`RA_ispiti_9_A_razred_Tehnicki_dio.pdf`](http://www.hamradio.hr/download/RA_ispiti_9_A_razred_Tehnicki_dio.pdf)
  — and the corresponding three P-class banks:
  [`RA_ispiti_10`](http://www.hamradio.hr/download/RA_ispiti_10_P_razred_Pravila_i_postupci.pdf)/[`11`](http://www.hamradio.hr/download/RA_ispiti_11_P_razred_HR_i_medjunarodni_propisi.pdf)/[`12`](http://www.hamradio.hr/download/RA_ispiti_12_P_razred_Tehnicki_dio.pdf).
  Published by HRS.
- **`Radiokomunikacije.pdf`** (`_ocr.pdf`) — HRS's 410-page official priručnik, ~2005.
  Authored by **Mladen Zadro, dipl. ing.**
  (voditelj/lead author), with co-authors **Ante Botica, dipl. ing.**, **dr. sc. Draško
  Marin**, and **Vladimir Štancl, ing.**, reviewed by **dr. sc. Zvonimir Jakobović** and
  **mr. sc. Željko Ulip**, and published by Hrvatski radioamaterski savez. HRS does not host
  this one publicly — it's out of print, and copies have circulated via places like this
  [forum.hr thread](https://www.forum.hr/showthread.php?t=1064885); linked here for context,
  not as an endorsed distribution channel. The `_ocr.pdf` variant the build pipeline actually
  reads (`quiz/build/booktool.py`'s `RK` source) is produced locally by running the original
  through [PDF24](https://tools.pdf24.org/)'s OCR tool to add a text layer — it is not a
  separately downloaded file.
- **[`ZBIRKA-1_Prirucnik-Radiokomunikacije-2023.pdf`](https://www.hamradio.hr/wp-content/uploads/2025/11/ZBIRKA-1_Prirucnik-Radiokomunikacije-2023.pdf)**
  — despite its filename this is a *different* work: "Priručnik praktičnih radova za
  pripremu natjecanja mladih tehničara u području radiokomunikacije" (2023), authored by
  **Jelena Tuksar, mag. ing.**, **mr. sc. Željko Ulip**, and **Stipe Predanić, dipl. ing.**,
  published by HRS.

### One externally-authored, out-of-print book

[`Pasaric_Radioamaterizam_za_mlade.pdf`](https://www.hamradio.hr/download/Pasaric_Radioamaterizam_za_mlade.pdf)
— *"Radioamaterizam za mlade — priručnik za polaganje operatorskog P-ispita"*, by **Božidar
Pasarić, 9A2HL**, Zagreb 2008, published in the University of Zagreb's official textbook
series ("Udžbenici Sveučilišta u Zagrebu" / *Manualia Universitatis Studiorum
Zagrabiensis*). Publisher of record: Hrvatski radioamaterski savez.

Every hamradio.hr link above was fetched this session and confirmed byte-identical to this
project's local copy.

---

## The self-improving system

**What's real today:** content work on this project runs through a small internal pipeline —
`queue/` holds one work item per file (`queue/QUEUE.md` is the contract), drained by the
`/drain` skill using worker and checker subagents so each change is independently reviewed
before landing. Two build-time guards backstop it: `rebuild.py` aborts rather than ship a
question with no valid answer, the wrong option count, an empty stem, or a duplicate id, and
`strict.py` re-runs the book-vs-HRS cross-check on every rebuild so an edit that breaks
agreement is caught immediately, not discovered by a test-taker.

Every question also carries a **"Prijavi problem"** button that opens a prefilled GitHub
issue (question id, current answer, citation, and a chosen reason), labelled `quiz-feedback`.
`queue/from_issues.py` turns each open one of those into a queue item at the start of every
`/drain` run and closes the issue as triaged — a reader spotting a mistake and a worked queue
item are the same closed loop, not two separate steps.

---

## License

- **Code** (the Python build pipeline under `quiz/build/`, and the generated quiz
  HTML/JS) — **MIT**, see [`LICENSE`](LICENSE).
- **Teaching notes and citations** (the content of `quiz/build/notes_*.json`) — these are
  Glaukon's own authored derivative work, and are **CC BY-SA 4.0**, see
  [`LICENSE-NOTES`](LICENSE-NOTES).
- **The underlying exam questions and answer keys** are HRS's own material, used here under
  citation. They are covered by neither license grant above; this project does not claim to
  license HRS's content, only its own code and notes.

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
