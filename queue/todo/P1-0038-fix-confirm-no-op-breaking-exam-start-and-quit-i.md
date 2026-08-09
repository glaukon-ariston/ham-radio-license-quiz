# Fix confirm() no-op breaking exam start and quit in sandboxed iframe

prio:       P1
cluster:    quiz-app-ui
files:      quiz/build/build_quiz.py
blocked-by:

**Why.** Glaukon reports that clicking "Simulacija ispita" does nothing, and that
"Prekini" during "Vježba" also does nothing, leaving no way back to the home
screen mid-session. Both handlers gate on `window.confirm(...)`
(build_quiz.py:636 `data-go="exam"`, and build_quiz.py:642 `$("#quit").onclick`).
The app's own comment at build_quiz.py:157-158 already notes it runs inside a
cross-origin sandboxed iframe on claude.ai. A sandboxed iframe without
`allow-modals` silently suppresses `alert`/`confirm`/`prompt` — the call
returns `undefined` (falsy) instead of throwing or showing a dialog, so
`if(confirm(...))` is always false there and the click appears to do nothing.
`$("#reset").onclick` (build_quiz.py:643) has the same `confirm()` pattern and
is likely broken the same way, just not reported yet.

**Done when.** All three call sites (start exam, quit, reset progress) use an
in-page confirmation (e.g. a small inline confirm state built with existing
DOM/CSS, not a native dialog) instead of `window.confirm`, and clicking
"Simulacija ispita", "Prekini", and "Obriši napredak" each work when the page
is loaded inside a sandboxed iframe with no `allow-modals` (test by loading
quiz.html in an `<iframe sandbox="allow-scripts allow-same-origin">` — no
`allow-modals` — and confirming all three actions still complete).

**Avoid.** Don't touch the exam timer/scoring logic or the `#quit` visibility
rule (`mode==="single"` hides it) — only the confirmation mechanism is broken.
Keep working correctly outside an iframe too (a plain browser tab does support
`confirm()`, so don't regress that path).
