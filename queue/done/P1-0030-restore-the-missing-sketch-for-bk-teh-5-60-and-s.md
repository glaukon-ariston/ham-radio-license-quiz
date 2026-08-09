# Restore the missing sketch for bk-teh-5-60 and strip the answer from its stem

prio:       P1
cluster:    book-figures
files:      quiz/build/book_overrides.json, quiz/build/book_figures.py, quiz/questions.json
blocked-by:

**Why.** `bk-teh-5-60` (RK, Ispitna pitanja SKUPINA V, pitanje 60, tiskana str. 343) is
unanswerable and self-spoiling at once. Its stem ends `... Sigurnosna udaljenost iznosi
6,4m. Potrebno je: 8m` — the trailing `8m` is OCR bleed off the sketch, and it hands over
key `b` ("umjesto desnog 4 m visokog stupa postaviti 8 m stup"). The sketch it says the
antenna is set up "kao na skici" was never cropped: only six book questions carry a
`figure`, and this is not one of them.

**Done when.** The stem reads as printed, with no `8m` tail and no other figure text in
it; `bk-teh-5-60` has a `figure` in `figs_book_index.json` and a PNG in `figs_book/`
showing the two masts and the wire; `figure_is_options` is false (the options are text);
the figure renders in `quiz.html`; and `rebuild.py` runs clean.

This is the pilot for the whole batch: it is the first *stem* figure ever cropped, and
0031 calibrates its window proposer against the window measured here.

**Avoid.** Do not touch the answer — key `b` comes from the book's own table and stands.
Read the crop window off the rendered page of `docs/Radiokomunikacije_ocr.pdf`, the way
the other six entries in `book_overrides.json` were taken; do not guess it. Keep the red
neutralisation in `figures2.postprocess` — the book marks correct answers in red. Record
the measured window in `queue/reports/0030.md` so 0031 can check against it.
