# Fix quiz UX/a11y gaps from UX_REVIEW.md

prio:       P2
cluster:    quiz-ux
files:      quiz/build/build_quiz.py, quiz/UX_REVIEW.md
blocked-by:

**Why.** A full UX/a11y design review of the quiz app (`quiz/UX_REVIEW.md`, written
13 Aug 2026) found the app is generally well-built but has three contained, high-value gaps:
keyboard/screen-reader users lose focus on every screen transition (#1), the correct/incorrect
answer after a practice question is signalled by color alone (#2, a WCAG 1.4.1 violation), and
the sticky header (brand + 2 selects + timer + quit) has no narrow-viewport plan and can
overflow on a phone during an exam (#3). Read `UX_REVIEW.md` in full before starting — it also
lists what NOT to touch (the palette system, `askConfirm()`, the exam-integrity gating in
`render()`, the reduced-motion query, the input-field guard on the keyboard handler) and *why*
each exists.

**Scope for this item is UX_REVIEW.md findings #1, #2, and #3 only** (the "High priority"
section). Findings #4–#8 (Medium) and #9–#11 (backlog/decide-only) are documented in the same
file for a future item — do not fold them into this one.

Remember all markup/CSS/JS for the live page lives in the `HTML = r"""..."""` template inside
`quiz/build/build_quiz.py`, not in `quiz/quiz.html` directly — `quiz.html` is generated output
(`python quiz/build/rebuild.py` regenerates it from the template + `questions.json`). Edit the
template, then rebuild; editing `quiz/quiz.html` by hand will be silently overwritten.

**Done when.**
1. `show(id)` in the built page moves keyboard focus to the target section's own heading on
   every transition (home→picker, home→quiz, quiz→result, result→home, etc.) — verifiable by
   tabbing through the whole home→practice→answer→finish path with a mouse untouched and
   confirming focus is never lost to `<body>`.
2. In practice mode, after answering, the correct option and (if applicable) the wrongly-picked
   option carry a non-color signal (glyph or text) in addition to their existing border/background
   color — verifiable by inspecting the rendered DOM for the `.ok`/`.no` option, or by viewing the
   page with a colorblindness simulator/grayscale filter and still being able to tell which
   option was correct.
3. The sticky header (brand, both selects, timer, quit button) no longer clips or forces
   horizontal page scroll at 360–390px viewport width with the timer and quit button both
   visible (i.e. simulating exam mode) — verifiable in a browser devtools responsive view.
4. `python quiz/build/rebuild.py` still ends with 1176 questions and no integrity failures;
   `python quiz/build/check_notes.py` and `python quiz/build/strict.py` still pass at their
   current baseline (they should be untouched by this change, since no `questions.json` or
   note content is involved).

**Avoid.** Do not touch `questions.json`, any `notes_*.json` file, `overrides.json`, or answer
content — this is a presentation-only change. Do not modify the palette/theme system, remove or
alter `askConfirm()`, weaken the exam-mode gate that hides `.ok`/`.no` until `finish()` (see
`UX_REVIEW.md` "What's already right"), or add continuous `aria-live` chatter on the exam timer
(a one-time announcement at the 5-minute mark, if attempted, is UX_REVIEW.md finding #5 —
out of scope here, skip it). Do not publish/update the live artifact — that stays a
human-triggered step per `queue/BRIEF.md`.
