# Draft README.md for public release

prio:       P2
cluster:    public-release
files:      README.md (new)
blocked-by:

**Why.** No README exists. Glaukon wants to publish this repo on GitHub for the Croatian
radioamateur community, crediting every source document and its authors/rightsholders, and
explaining the project's self-improving design. Plan agreed 13 Aug 2026; write it now.

**Content, and the research behind each section (a cold worker should not have to
re-derive this):**

1. **Pitch + status.** 1176-question A-class exam practice quiz, built from HRS's own
   answer-marked exam banks. Link to the live GitHub Pages quiz once it exists (P2-0058) —
   until then, write `**Try it:** _(link goes live once GitHub Pages is set up — see
   P2-0058)_` rather than inventing a URL.

2. **How it's built.** Briefly: HRS's exam PDFs mark correct answers in red text, invisible
   to `pdftotext` but readable via PyMuPDF; cross-validated against the 2005 book
   (`Radiokomunikacije.pdf`) at 95.3% agreement; every question carries a cited teaching
   note. Source this from `QUIZ_PLAN.md` — don't re-derive, just summarize accurately.

3. **Sources & acknowledgments — list every file in `docs/`, in three tiers** (verified by
   reading each PDF's own text/metadata this session):
   - **Public regulatory/institutional texts** — Pravilnik o amaterskim radijskim
     komunikacijama (NN 150/22), CEPT T/R 61-01 and 61-02, ERC Report 32, and the HRS/HAKOM
     *Odluka* / decision documents (`RA_ispiti_1..4`, `HAKOM_Dopunsko_rjesenje_P_razred`).
     Link each to its official source (e.g. narodne-novine.nn.hr for the Pravilnik) rather
     than redistributing — **fetch and confirm every link actually resolves to that
     document before citing it**, per `queue/BRIEF.md` rule 2.
   - **HRS's own exam & instructional material** — the three A-class banks
     (`RA_ispiti_7/8/9`) and three P-class banks (`RA_ispiti_10/11/12`); `Radiokomunikacije.pdf`
     / `_ocr.pdf`, the 410-page official priručnik, credited to **Hrvatski radioamaterski
     savez (HRS)** as publisher — it names no individual author, only "izdaje Hrvatski
     radioamaterski savez" (confirmed by reading its own intro pages; do not invent an
     author). Also `ZBIRKA-1_Prirucnik-Radiokomunikacije-2023.pdf` — despite its filename
     this is a *different* work, "Priručnik praktičnih radova za pripremu natjecanja mladih
     tehničara u području radiokomunikacije" (2023), authored by **Jelena Tuksar mag.ing.,
     mr.sc. Željko Ulip, and Stipe Predanić dipl.ing.**, published by HRS — confirmed from
     its own title page (page 0/2 of the PDF).
   - **One externally-authored, out-of-print book** — `Pasaric_Radioamaterizam_za_mlade.pdf`,
     *"Radioamaterizam za mlade — priručnik za polaganje operatorskog P-ispita"*, by
     **Božidar Pasarić, 9A2HL**, Zagreb 2008, published in the University of Zagreb's
     official textbook series ("Udžbenici Sveučilišta u Zagrebu" — confirmed from page 3 of
     the PDF). Credit him and the press by name.
   - State plainly: none of these files are redistributed in this repo (see P1-0055/0056);
     this section exists to credit sources and tell readers how to obtain them, not to host
     them.

4. **The self-improving system — describe honestly, don't overclaim.** What's real today:
   `queue/` + the `/drain` skill + worker/checker subagents, `rebuild.py`'s abort-on-bad-data
   guard, `strict.py`'s book-vs-HRS cross-check — this is a working internal content
   pipeline, summarize it from `queue/QUEUE.md` and `queue/BRIEF.md`. What's *not* built yet:
   there is no in-quiz feedback UI and no automated issue→queue-item pipeline for public
   users (confirmed: `quiz/quiz.html` has no feedback-submission code, only a comment
   suppressing feedback during exam mode). Present that second part as direction/roadmap,
   explicitly labeled as not yet implemented.

5. **License.** State: MIT for the code (Python build pipeline, quiz HTML/JS); CC BY-SA for
   the original teaching notes/citations (`quiz/build/notes_*.json` content) as Glaukon's own
   authored derivative work; and note explicitly that the underlying HRS exam questions and
   answer keys remain HRS's own material, used here under citation, not covered by either
   license grant. Do not add SPDX `LICENSE` files in this item — just state the intent in
   the README; a separate item can add formal license files later if wanted.

6. **Origin story.** Link `PLAN.md` and `QUIZ_PLAN.md` as-is — "this grew out of one
   person's own A-class exam prep" — per Glaukon's explicit choice (13 Aug 2026) to keep
   them public rather than trim the personal pico-balloon content out.

7. **Disclaimer.** Unofficial project, not affiliated with or endorsed by HRS or HAKOM;
   answer accuracy is tied to HRS's own published key.

**Done when.** `README.md` exists at the repo root with all seven sections above, every
fact in it checked against the actual current repo state (not invented or copied from this
item without verifying it's still true), and every external link fetched and confirmed to
resolve to the right document (not just HTTP 200 — check what the page *is*, per BRIEF.md
rule 2).

**Avoid.** Don't claim the public feedback→issue→queue loop is built when it isn't. Don't
invent an individual author for `Radiokomunikacije.pdf` — it has none, only HRS as
publisher. Don't reference or link to the raw `docs/` files as if they ship in this repo.
Don't touch `PLAN.md`/`QUIZ_PLAN.md` content itself, only link to them.
