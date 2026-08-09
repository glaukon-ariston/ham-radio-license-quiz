# Restore book stem figures: skupina I

prio:       P2
cluster:    book-figures
files:      quiz/build/book_overrides.json, quiz/build/book_figures.py, quiz/build/figs_book/
blocked-by: 0031

**Why.** 9 questions in SKUPINA I — tehnički (tiskane str. 288–295) show a schematic,
curve or oscillogram between the stem and the options, and none of them has been cropped.
They currently render as text alone, which for stems like `"Filtar na slici je:"` means
unanswerable. `bk-teh-1-12` is already in `book_overrides.json` for a different reason
(merged-block) and needs a `figure` key added, not a new entry.

**Done when.** Every id 0031 lists for skupina I has a `figure` window in
`book_overrides.json`, a PNG in `figs_book/`, and an entry in `figs_book_index.json`;
each crop was opened and seen to contain the whole picture and no option text; any OCR
debris the figure left in the stem is gone; `fig_audit.py` reports nothing outstanding for
skupina I; `rebuild.py` still reports 1176 questions.

**Avoid.** `figure_is_options` is false for all of these — the options are text and stay
text. Never touch an answer: keys come from `book_keys.json` by position. Keep the red
neutralisation in `figures2.postprocess`; the book prints some correct answers in red and
an un-neutralised crop hands them over.
