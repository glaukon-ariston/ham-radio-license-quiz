# Restore book stem figures: skupina IV

prio:       P2
cluster:    book-figures
files:      quiz/build/book_overrides.json, quiz/build/book_figures.py, quiz/build/figs_book/
blocked-by: 0031

**Why.** 14 questions in SKUPINA IV — tehnički (tiskane str. 322–329) show a picture
between the stem and the options. Three of them — `bk-teh-4-07`, `bk-teh-4-08`,
`bk-teh-4-36` — already have one, so 11 are outstanding. `bk-teh-4-48` is in
`book_overrides.json` for another reason and needs a `figure` key added to the existing
entry.

**Done when.** Every id 0031 lists for skupina IV has a `figure` window in
`book_overrides.json`, a PNG in `figs_book/`, and an entry in `figs_book_index.json`;
each crop was opened and seen to contain the whole picture and no option text; any OCR
debris the figure left in the stem is gone; `fig_audit.py` reports nothing outstanding for
skupina IV; `rebuild.py` still reports 1176 questions.

**Avoid.** The three existing figures are correct — do not recrop them, and do not flip
their `figure_is_options`, which is true because their options really are diagrams.
Everything you add here has it false. Never touch an answer. Keep the red neutralisation
in `figures2.postprocess`.
