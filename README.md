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

This quiz started from HRS's own material. HRS publishes six separate exam-question banks:
three for the **A-class** licence this project targets (*Tehnički dio*, *HR i međunarodni
propisi*, *Pravila i postupci*) and three parallel ones for the lower **P-class** licence. P's
syllabus is a strict subset of A's — same topics, a smaller and simpler slice of them — so this
project only draws from the three A-class banks; the P-class ones add nothing an A-class holder
doesn't already cover. Every question in those three banks carries the correct answer marked in
red in HRS's own PDF. That's the exam-authoritative core — **456 questions**, each carrying
HRS's own marked answer.

We complemented that with a much bigger source: **`Radiokomunikacije.pdf`**, HRS's own
~2005 study manual and the official reference text for the A exam. It covers far more ground
than the 456-question bank and has its own answer-key tables, which added **720** further
practice questions — for **1176** total.

Turning the PDFs into structured question data needed a purpose-built parser, not a plain text
dump. The usual `pdftotext` extraction discards colour entirely, so it can't see the red answer
marks at all. Reading the PDFs with PyMuPDF instead recovers that colour and, as a bonus, fixes
the Croatian diacritics (č/ć/ž/š) that `pdftotext` mangles. The book has no native text layer —
it's a 410-page scan — so its questions come from an OCR pass instead; but OCR reading order
emits the question-number column separately from the body text and regularly drops or garbles
numbers, so `parse_book2.py` parses by page *coordinates* instead, matching each number to its
question by position rather than trusting OCR's left-to-right guess.

Even with that parser, a few hundred entries still needed an LLM to do the actual reading: the
book's ~8 answer-key pages (grids of single letters, where one slip would silently poison dozens
of answers) and the 31 of 720 book questions the parser couldn't cleanly reach. The two sources
were then cross-checked against each other: on questions that exist in both, HRS's and the
book's answers agree 96.3% of the time (104/108) — every disagreement is a real change between
2005 and today, not an extraction error (see `quiz/REVIEW.md`).

On top of the question bank, we used an LLM to write a **teaching note for every one of the
1176 questions**. Each note doesn't just explain why the correct answer is right — it walks
through why every *other* option is wrong, so a lucky guess turns into an actual understanding
of the distinction. For numeric questions that means a worked formula with real numbers
substituted in; for regulatory ones it means the specific article of the relevant Pravilnik or
Odluka, not just "see the rulebook." Most notes also link out — to Croatian and English
Wikipedia articles for background, and to the exact page of HRS's or the book's own source
material the note is drawn from — so a wrong answer comes with both an explanation and a way to
go deeper.

The whole corpus rebuilds from the source PDFs in one command:

```bash
python quiz/build/rebuild.py
```

See `QUIZ_PLAN.md` for the full method, including the parser quirks (two-column option
layout, symbol-font glyphs, relettered options) and the two hazards documented there: the
book is legally out of date on regulatory matters, and answer *letters* can't be copied
across sources — only option *text* can.

---

## The self-improving system

This project was built with an AI coding assistant doing the actual technical work — reading
PDFs, writing parsers, extracting questions, writing teaching notes, designing and building
the quiz's UI, fixing bugs. The ordinary way to work with one is a chat window: you ask for
one thing, wait for it to finish, look it over, then ask for the next. That's fine for an
afternoon's work, but this project runs over a thousand questions, each needing extraction,
cross-checking, and a teaching note, on top of a quiz interface that took its own rounds of
iterating and experimenting to get right — waiting on every single step one at a time would
have made the whole project far slower than it needed to be.

So instead, the work is written down first. Every feature, fix, or content task becomes a
small markdown file describing what needs doing and why, and those files sit in a queue
(`queue/`, one file per work item — `queue/QUEUE.md` is the contract). A skill called `/drain`
then works through that queue on its own: it picks a work item, hands it to a worker subagent
to make the change, then hands the result to a separate checker subagent — kept read-only on
purpose, so it can review the work without being able to alter it — before anything is
allowed to land. The moment one work item is done, `/drain` moves to the next, without anyone
needing to sit and watch each step finish before starting the next one. That's the actual
payoff: the assistant stays busy on a backlog instead of idling between chat turns, so more
of the project gets built in the same amount of time. This same queue is used for both
building new quiz features and fixing bugs — the two are just different kinds of work item.

Quality still has to be enforced, though, not assumed. The source material and every step of
turning it into a quiz question have their own failure points — PDF-to-text conversion
errors, OCR misreads, parser edge cases — on top of the ordinary risk of a citation going
stale or the exam key changing. Two build-time guards catch that: `rebuild.py` aborts rather
than ship a question with no valid answer, the wrong option count, an empty stem, or a
duplicate id, and `strict.py` re-runs the book-vs-HRS cross-check on every rebuild, so an
edit that breaks agreement between the two sources is caught immediately, not discovered by
a test-taker.

Once that pipeline existed for building the quiz, it made sense to point it at the quiz's own
readers too. However careful the pipeline is, something can still end up wrong in the
finished quiz — a question or its teaching note traces back through PDF conversion, OCR, and
parsing before an LLM ever sees it, any one of those steps can misread something, and even a
perfectly-extracted question can go stale later if the exam key changes. So every question
carries a **"Prijavi problem"** button, where a reader picks the kind of problem they found
— a wrong answer, a bad or outdated citation, a typo or unclear wording, a missing or wrong
figure, or something else — and it opens a prefilled GitHub issue with the question id, the
current answer, its citation, and that reason, labelled `quiz-feedback`. At the start of
every `/drain` run, `queue/from_issues.py` turns each open one of those into a work item and
closes the issue as triaged. A reader spotting a mistake and a worked queue item end up being
the same closed loop, not two separate steps.

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
text layer). The CEPT/ERC documents originate with CEPT/ECC; they're linked here via HRS's own
download page (`hamradio.hr`) because that's HRS's own published source for exam candidates,
not CEPT's own site.

### HRS's own exam & instructional material

- **The three A-class question banks** —
  [`RA_ispiti_7_A_razred_Pravila_i_postupci.pdf`](http://www.hamradio.hr/download/RA_ispiti_7_A_razred_Pravila_i_postupci.pdf),
  [`RA_ispiti_8_A_razred_HR_i_medjunarodni_propisi.pdf`](http://www.hamradio.hr/download/RA_ispiti_8_A_razred_HR_i_medjunarodni_propisi.pdf),
  [`RA_ispiti_9_A_razred_Tehnicki_dio.pdf`](http://www.hamradio.hr/download/RA_ispiti_9_A_razred_Tehnicki_dio.pdf)
  — and the corresponding three P-class banks:
  [`RA_ispiti_10`](http://www.hamradio.hr/download/RA_ispiti_10_P_razred_Pravila_i_postupci.pdf)/[`11`](http://www.hamradio.hr/download/RA_ispiti_11_P_razred_HR_i_medjunarodni_propisi.pdf)/[`12`](http://www.hamradio.hr/download/RA_ispiti_12_P_razred_Tehnicki_dio.pdf).
  Published by HRS.
- **`Radiokomunikacije.pdf`** (`_ocr.pdf`) — HRS's official study material for the A-class
  exam: a 410-page priručnik, ~2005. Authored by **Mladen Zadro, dipl. ing.**
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
