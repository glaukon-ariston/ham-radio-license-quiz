# Restore book stem figures: skupina II

prio:       P2
cluster:    book-figures
files:      quiz/build/book_overrides.json, quiz/build/book_figures.py, quiz/build/figs_book/
blocked-by: 0031

**Why.** 14 questions in SKUPINA II — tehnički (tiskane str. 298–308) show a picture
between the stem and the options and none has been cropped, so stems like
`"Sklop na slici je:"` render unanswerable. Three — `bk-teh-2-04`, `bk-teh-2-06`,
`bk-teh-2-07` — are already in `book_overrides.json` as merged-blocks and need a `figure`
key added to the existing entry, not a second one. `bk-teh-2-07` refers to "transformator T
na slici iz pitanja 6", so it shares 2-06's picture: crop it twice rather than making the
renderer chase a reference.

**Done when.** Every id 0031 lists for skupina II has a `figure` window in
`book_overrides.json`, a PNG in `figs_book/`, and an entry in `figs_book_index.json`;
each crop was opened and seen to contain the whole picture and no option text; any OCR
debris the figure left in the stem is gone; `fig_audit.py` reports nothing outstanding for
skupina II; `rebuild.py` still reports 1176 questions.

**Avoid.** `bk-teh-2-20` and `bk-teh-2-46` already have figures and are figure-*options*
questions — leave both alone. `figure_is_options` is false for everything you add here.
Never touch an answer. Keep the red neutralisation in `figures2.postprocess`.
