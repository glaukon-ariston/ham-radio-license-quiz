# Transcribe bk-teh-2-03 as a figure-options question

prio:       P2
cluster:    book-figures
files:      quiz/build/book_overrides.json, quiz/build/book_figures.py, quiz/build/figs_book/
blocked-by:

**Why.** `bk-teh-2-03` (page 293, printed 298) is mis-parsed: the parser glued Q3's own
stem ("Koja od skica predstavlja filtar...") to Q4's stem ("Sklop na slici je:") and
assigned **Q4's text options** (`detektor ovojnice` / `ratio detektor` / `AM – detektor` /
`punovalni ispravljač`) to Q3. Q3's real answer choices are four labelled filter-response
sketches `a)`–`d)` printed under its stem — this is a `figure_is_options` case, same shape
as the existing `bk-teh-2-20`/`bk-teh-2-46` overrides, not a missing-stem-crop case. It
surfaced as the one id P2-0033 explicitly declined to touch (see `queue/reports/P2-0033.md`,
recovered from `git stash list` under the message `queue P2-0033: fail` — read it, the
prior worker already rendered page 293 at 200dpi and confirmed the four sketches by eye).

**Done when.** `book_overrides.json` has a `bk-teh-2-03` entry with the real stem, the
four picture-sketch options cropped into `figs_book/`, and `figure_is_options: true`;
`fig_audit.py` no longer lists `bk-teh-2-03` as outstanding; `rebuild.py` still reports
1176 questions and no integrity failures.

**Avoid.** Do not reuse Q4's options — they belong to `bk-teh-2-04`, which is already
correctly entered and must not change. Keep the answer key positional (from
`book_keys.json`), not re-derived from physics.
