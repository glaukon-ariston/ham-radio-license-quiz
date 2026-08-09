# Restore book stem figures: skupina V

prio:       P2
cluster:    book-figures
files:      quiz/build/book_overrides.json, quiz/build/book_figures.py, quiz/build/figs_book/
blocked-by: 0031

**Why.** 17 questions in SKUPINA V — tehnički (tiskane str. 332–343) show a picture
between the stem and the options. `bk-teh-5-60` is handled by 0030 as the pilot; follow the
window it measured by hand rather than re-deriving it. `bk-teh-5-49` asks about "elementi
L,C,R na slici u 48.zadatku", so it shares 5-48's picture — crop it twice rather than making
the renderer chase a reference. `bk-teh-5-44` is already in `book_overrides.json` and needs
a `figure` key added to the existing entry.

**Done when.** Every id 0031 lists for skupina V has a `figure` window in
`book_overrides.json`, a PNG in `figs_book/`, and an entry in `figs_book_index.json`;
each crop was opened and seen to contain the whole picture and no option text; any OCR
debris the figure left in the stem is gone — `bk-teh-5-04` ends `— IE HB o` today;
`fig_audit.py` reports nothing outstanding for skupina V; `rebuild.py` still reports 1176
questions.

**Avoid.** `bk-teh-5-52` already has a figure and is a figure-*options* question — leave it
alone. `figure_is_options` is false for everything you add here. Never touch an answer.
Keep the red neutralisation in `figures2.postprocess`.
