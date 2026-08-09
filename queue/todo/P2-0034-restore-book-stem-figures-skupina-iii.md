# Restore book stem figures: skupina III

prio:       P2
cluster:    book-figures
files:      quiz/build/book_overrides.json, quiz/build/book_figures.py, quiz/build/figs_book/
blocked-by: 0031

**Why.** 19 questions in SKUPINA III — tehnički (tiskane str. 309–319) show a picture
between the stem and the options and none has been cropped. This is the worst batch for
OCR debris: `bk-teh-3-06` ends `"3`, `bk-teh-3-16` ends `HI no`, `bk-teh-3-51` ends `—`,
`bk-teh-3-53` ends `stHHIr&=e` — all of it text the figure shed into the stem. `bk-teh-3-44`
and `bk-teh-3-45` are already in `book_overrides.json` and need a `figure` key added to the
existing entry.

**Done when.** Every id 0031 lists for skupina III has a `figure` window in
`book_overrides.json`, a PNG in `figs_book/`, and an entry in `figs_book_index.json`;
each crop was opened and seen to contain the whole picture and no option text; the stems
above read as printed with the debris gone; `fig_audit.py` reports nothing outstanding for
skupina III; `rebuild.py` still reports 1176 questions.

**Avoid.** `bk-pra-3-04` (tiskana str. 387) trips 0031's gap detector but has no picture —
it is a long call-sign stem, and it is the one known false positive. Do not crop it.
`figure_is_options` is false throughout. Never touch an answer. Keep the red neutralisation
in `figures2.postprocess`.
