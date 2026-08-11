# Book notes never reach the live quiz - byid excludes extra in rebuild.py

prio:       P1
cluster:    build-pipeline
files:      quiz/build/rebuild.py
blocked-by:

**Why.** `quiz/build/rebuild.py:111` builds `byid = {q["id"]: q for q in hrs}` — `hrs` only,
never `extra` (the 720 book-only `bk-*` questions in `questions_extra`). The "attach
explanations" loop right below it looks every note up in `byid`, so every `notes_book_*.json`
entry — the entire P3-00xx book-notes project, dozens of items marked done across weeks of
work — silently lands in the printed "notes for unknown ids" list and is dropped. Confirmed
by running the build: `explained=456` out of 1176 questions, i.e. 0 of the 720 book notes
that have actually been authored are making it into `quiz/questions.json`. Glaukon has been
reading questions off the built quiz expecting notes (e.g. `bk-teh-2-15`, `bk-pro-1-19`,
`bk-teh-4-19`) that were in fact written long ago and are just not shown.

**Done when.** The explanation-attach loop covers both `hrs` and `extra` (e.g.
`byid = {q["id"]: q for q in hrs + extra}`, built after `extra` exists). `rebuild.py` prints
no "notes for unknown ids" for any `bk-*` id that has an entry in some `notes_book_*.json`.
`explained` count in the rebuild summary rises from 456 to roughly 456 + (however many
`bk-*` notes currently exist across `notes_book_*.json`), and `quiz/questions.json`'s
`questions_extra` entries carry their `explanation` field. Re-run `strict.py` and confirm the
pass rate does not regress.

**Avoid.** Don't touch the `notes_*.json` content itself — the notes are fine, only the merge
is broken. Watch the ordering: `extra` is built (with citations, figures) well before line
111, so folding it into `byid` there is safe, but double check nothing between `extra`'s
construction and line 111 depends on `byid` being HRS-only. This is a one-line-shaped fix;
resist the urge to also "clean up" the surrounding block.
