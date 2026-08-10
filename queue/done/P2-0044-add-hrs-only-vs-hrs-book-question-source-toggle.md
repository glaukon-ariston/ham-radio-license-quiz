# Add HRS-only vs HRS+book question source toggle

prio:       P2
cluster:    quiz-app-ui
files:      quiz/quiz.html
blocked-by:

**Why.** `questions.json` already splits the corpus into `questions` (456 live HRS exam
questions) and `questions_extra` (720 book-derived questions, see
[[ham-quiz-corpus-complete]]). The quiz UI currently has no way to pick between "HRS
exam bank only" and "HRS + book" when starting practice or a simulated exam, so users
can't practice against just the real exam pool or opt into the larger combined set.

**Done when.** Both the practice-question picker and the simulated-exam start screen offer
a source choice — HRS only (~456) vs HRS + book (~1176) — the choice restricts which pool
questions are drawn from, and the counts shown to the user match whichever pool is active.

**Avoid.** Don't change how `subsection`/`cjelina` filtering works — this is an orthogonal
axis (source pool) layered on top of it, not a replacement. Simulated-exam scoring/pass
threshold logic must stay tied to the real HRS exam structure regardless of which pool
supplied the questions.
