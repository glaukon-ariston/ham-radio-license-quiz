# Restore book stem figures: skupina VI

prio:       P2
cluster:    book-figures
files:      quiz/build/book_overrides.json, quiz/build/book_figures.py, quiz/build/figs_book/
blocked-by: 0031

**Why.** 9 questions in SKUPINA VI — tehnički (tiskane str. 344–351) show a picture between
the stem and the options and none has been cropped. None of them is in
`book_overrides.json` yet, so each needs a fresh entry carrying `page`, `reason`, `figure`
and the transcribed stem. `bk-teh-6-14` ("dijagram zračenja rezonancijske antene
postavljene na visini / = 2 2. iznad") also needs its stem repaired — the height is an OCR
mangling of a wavelength expression, readable only off the page.

**Done when.** Every id 0031 lists for skupina VI has a `figure` window in
`book_overrides.json`, a PNG in `figs_book/`, and an entry in `figs_book_index.json`;
each crop was opened and seen to contain the whole picture and no option text; any OCR
debris the figure left in the stem is gone; `fig_audit.py` reports nothing outstanding for
skupina VI; `rebuild.py` still reports 1176 questions.

**Avoid.** `figure_is_options` is false throughout — the options here are text. Never touch
an answer; keys come from `book_keys.json` by position, and a new override changes option
*order* at your peril. Keep the red neutralisation in `figures2.postprocess`.
