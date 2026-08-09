# Turn the in-quiz breadcrumb into practice entry-point links

prio:       P2
cluster:    quiz-app-ui
files:      quiz/build/build_quiz.py
blocked-by:

**Why.** Glaukon asked for the breadcrumb shown while answering a question
(`#qcrumb`, built in `render()` at build_quiz.py:344-357, e.g. "Tehnički
sadržaj · Odašiljači (predajnici)") to become two clickable entry points: one
for the whole section and one for the specific cjelina. Right now it's plain
text appended via `.append()`, with no navigation. `start("practice",
{filter})` (build_quiz.py:313) already supports filtering by `q.s===k` or
`q.sub===name` — `buildPicker()` and the home `subTable` row buttons
(build_quiz.py:526-530, 556-559) are existing examples of the same pattern.

**Done when.** In quiz/practice views (not exam — `S.mode === "exam"` must
keep the breadcrumb as inert text exactly as the neighbouring `q.id` permalink
already does at build_quiz.py:354-356, so a running exam attempt can't be
navigated away from accidentally), the section name in `#qcrumb` is a link
that calls `start("practice", {filter: q => q.s === q.s})` for the current
section, and, when `q.sub` is set, the cjelina name is a second link that
filters on `q.sub`. Clicking either starts a new practice session scoped
accordingly. Verify by opening a tehnički question outside exam mode and
clicking both breadcrumb parts.

**Avoid.** Don't change breadcrumb behaviour during an active exam (mode ===
"exam") — it must stay non-interactive there, same as the id tag already is.
Propisi/pravila questions have `q.sub` unset, so only render one link (the
section) for those; don't invent subsection names here — see item 0040's
scope note on why that data doesn't exist.
