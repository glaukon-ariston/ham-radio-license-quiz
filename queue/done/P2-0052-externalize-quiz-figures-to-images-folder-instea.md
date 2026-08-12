# Externalize quiz figures to images/ folder instead of base64-inlining

prio:       P2
cluster:    quiz-load-time
files:      quiz/build/build_quiz.py, quiz/build/rebuild.py, quiz.html, quiz/images/ (new)
blocked-by:

**Why.** `quiz.html` is 12.4MB; measured breakdown shows 135 base64-inlined PNG figures
account for 10.3MB (83%) of that, while all 1176 questions' text (question/options/
explanation/formula/citations/links) is only ~2.1MB. The PNGs already exist as plain files
in `build/figs/` and `build/figs_book/` before `rebuild.py`'s base64-inlines them into
`questions.json` (and from there into the `f` field of the packed `DATA` payload in
`build_quiz.py`). Every page load re-parses all 10.3MB of base64 as part of one giant JS
object literal, even though only one figure is ever displayed at a time
(`$("#qimg").src = q.f`, quiz.html ~line 528).

**Done when.** `build_quiz.py`'s `pack()` emits `f` as a relative path (e.g.
`"images/teh-024.png"`) instead of a base64 data URI, the one runtime line that sets
`#qimg`'s src is updated to use that path, and `rebuild.py` gains a step that copies the
needed PNGs from `build/figs/` + `build/figs_book/` into `quiz/images/` alongside
`quiz.html`. After `python quiz/build/rebuild.py`, `quiz.html` is ~2.1MB (down from
~12.4MB), figures still render correctly for every question that has one (spot-check a
few `teh-*` and `bk-*` ids with figures in a browser), and `python quiz/build/strict.py`
does not regress. Must work both opened directly as `file://` (double-click) and served
over `http(s)://` — `<img src="images/...">` satisfies both, unlike `fetch()`, which is
CORS-blocked for local files under `file://`.

**Avoid.** Do not touch `figure_is_options`/`fo` handling or any other DATA field — only
the `f` field's representation changes, not how it's used elsewhere. Do not attempt
gzip/on-demand-chunk loading in this item; those were discussed as separate, lower-ROI
follow-ups and are out of scope here. `quiz.html` stops being copy-pasteable as a single
standalone file once this lands (it needs its sibling `images/` folder) — that's an
accepted tradeoff, not a bug to work around.
