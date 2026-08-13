# UX / UI design review — quiz/quiz.html

Written 13 August 2026. Scope: the quiz application itself (`quiz/quiz.html`, built by
`quiz/build/build_quiz.py`) — visual design, interaction design, accessibility, responsive
behaviour. Not in scope: question content, citations, or answer-key correctness (see
`REVIEW.md`/`NEXT_SESSION.md` for that). Method: read the full CSS, markup and script
(886 lines, one 2.1&nbsp;MB inline `const DATA` line excepted), traced every interactive path
(home → practice picker → quiz → result, exam mode, wrong-queue review, deep links, the
in-page confirm dialog), and checked against WCAG 2.1 AA where it applies to a single-page
quiz app.

## Bottom line

This is an unusually well-built single-file app for what it is. Someone already solved the
hard, easy-to-miss problems: a verified-contrast theme system (3 palettes × light/dark, 6
combinations, with a code comment stating the pairs were checked against WCAG before the
hexes were picked), a hand-rolled confirm dialog because `window.confirm()` silently no-ops
inside the sandboxed iframe this runs in on claude.ai, exam-integrity guards (no answer
reveal until the end, a running exam can't be derailed by a stray hash change), full keyboard
support that correctly gets out of the way when focus is in a text field, and a permalink /
lookup system built specifically to work around the fact that a `#` fragment on the parent
page never reaches a cross-origin iframe. None of that is default behaviour — it was each
solved on purpose, and none of it should be touched incidentally while making the changes
below.

The gaps that remain cluster in three places: **keyboard/screen-reader users lose their
place on every screen transition**, **the one moment that matters most for a colorblind
user — which option was actually correct — is color-only**, and **the sticky header has no
narrow-viewport plan**. All three are contained, low-risk fixes that don't touch `DATA`,
the build pipeline, or any question content.

## What's already right — don't change these while fixing the rest

- The palette system (`:root[data-palette]` × `prefers-color-scheme` × `[data-theme]`)
  composes cleanly; the code comments explain *why* each block exists. Any new component
  should read CSS variables, never hard-code a color.
- `askConfirm()` replacing `window.confirm()`/`alert()` — required because this page runs in
  a sandboxed iframe without `allow-modals` on claude.ai (see the comment at quiz.html:745).
  Don't reintroduce a native `confirm()`/`alert()` call anywhere.
- The document-level `keydown` handler explicitly bails out when `e.target` is an
  `INPUT`/`TEXTAREA`/`SELECT`/content-editable (quiz.html:874-877) so the 1–4/Enter shortcuts
  never fight the lookup box. Any new shortcut must respect the same guard.
- `@media (prefers-reduced-motion: reduce)` disables all transitions/animations globally
  (quiz.html:209) — keep any new animation inside that query's reach.
- Exam mode never applies `.opt.ok`/`.opt.no` until `finish()` (quiz.html:519, gated on
  `it.done`, which for exam mode only becomes true at the very end) — no answer leaks mid-exam.
  Any change to `render()` must preserve that gate.

## Findings and proposed changes

### High priority — accessibility, low risk, no data touched

**1. Screen transitions don't move focus.**
`show(id)` (quiz.html:780) toggles `.hidden` on the four top-level sections and scrolls to
top, but never moves keyboard focus. When a mode card inside `#home` is clicked and `#home`
becomes `display:none`, the browser drops focus to `<body>` — a keyboard or screen-reader
user gets no signal that anything happened, and has to explore the page from scratch to find
where they landed. This happens on every single navigation: starting a quiz, finishing one,
opening the picker, following a citation link back.

*Proposed change:* give each section's `h1`/`h2` (or a dedicated heading) `tabindex="-1"`,
and in `show(id)` call `.focus({preventScroll:true})` on the target section's heading right
after the `classList.toggle` loop. This is the single highest-value fix in this review —
contained to `show()`, ~4 lines, touches no other function.

**2. Correct/incorrect answer is color-only.**
After answering in practice mode, the right option gets `.opt.ok` and (if wrong) the picked
option gets `.opt.no` — both purely a border/background color change plus a color change on
the tiny `.k` letter marker (quiz.html:148-149, applied at quiz.html:521-522). Nothing in the
text content changes. For a deuteranopia/protanopia user (≈8% of men), green-on-card and
red-on-card at this saturation can be hard to tell apart at a glance, and this is the one
moment in the whole app where getting the distinction right actually matters. It's a WCAG
1.4.1 (Use of Color) violation as written.

*Proposed change:* in `render()`, when adding `.ok`/`.no`, also prepend a glyph to the `.k`
span's text — e.g. `✓` for the correct option, `✗` for a wrongly-picked one — or append
`(točno)`/`(tvoj odgovor)` as visually-hidden text for screen readers if a bare glyph feels
too busy. Either is a few lines inside the existing `it.order.forEach` loop at quiz.html:513.

**3. Sticky header has no narrow-viewport plan.**
`.barin` (quiz.html:83) is a single-row flex with no `flex-wrap` and no breakpoint: brand +
"Izvor pitanja" select + "Boje sučelja" select + timer + quit button all have to fit one row.
The two `<select>` elements' visible option text is long — "HRS + priručnik (1176)" is the
longest — and native selects size to their content on most browsers. On a ~360–390px phone
in exam mode (timer *and* quit button both visible, the worst case), this row is tight enough
to clip or force the page into horizontal scroll, which the rest of the layout deliberately
avoids (`.tscroll`/`.fx` scroll internally precisely so the page itself never does).

*Proposed change:* add a breakpoint (e.g. `@media (max-width:480px)`) that either (a) shrinks
the select labels to short forms ("HRS", "HRS+kn.") below that width via a second `<option>`
text set in JS, or (b) collapses both selects behind a single icon-button that opens the
confirm-style overlay already built for `askConfirm()`. (a) is the smaller change.

### Medium priority

**4. No `<main>` landmark, no section labelling.**
The four screens (`#home`, `#picker`, `#quiz`, `#result`) sit directly in `.wrap` with no
`<main>` wrapper and no `aria-labelledby`/`role` distinguishing them for assistive tech.
Adding `<main>` around `.wrap`'s contents and `aria-labelledby` on each `<section>` pointing
at its own heading id is a markup-only change that pairs naturally with finding #1 (the same
headings gain `tabindex="-1"` for focus and an id for labelling in one pass).

**5. No accessible signal at the exam time warning.**
`#tick` gets a `.warn` class under 5 minutes (quiz.html:453) — a purely visual color change.
A screen-reader user taking a timed exam gets no announcement at all. Continuous
`aria-live` on a per-250ms-updating timer would be unusable noise, so: add a separate
`aria-live="polite"` region that's normally empty and gets a one-time "Preostalo 5 minuta."
message written into it exactly when `.warn` first turns on (guard with a flag so it fires
once, not every tick).

**6. Figure alt text is one fixed string for all 52+ images.**
`<img id="qimg" alt="Slika uz pitanje">` (quiz.html:318) never changes — every diagram, every
question, same alt text. A screen-reader user practicing a circuit-diagram question gets no
more information than "image with question," every time. Writing a real description per image
isn't practical (many diagrams *are* the question, and describing one risks describing the
answer), but the alt text can at least vary by id/topic for orientation — e.g. build it from
the question id and section name in `render()` rather than hard-coding one sentence in markup.

**7. Home screen has no first-run state.**
`#home` shows the three mode cards, then unconditionally renders `secTable`, `subTable`, and
a history table (quiz.html:278-289) — all populated from `store`, which is empty on a brand
new visitor. A first-time user sees two tables full of "—" and "0" and an empty history
placeholder before they've done anything, which reads as broken or unfinished rather than
"nothing here yet." This isn't a bug — `home()` already handles the empty state correctly per
cell — it's a first-impression ordering problem.

*Proposed change:* nothing structural needs to move (subject-matter order — Gradivo, Po
cjelinama, Zadnji ispiti — is reasonable and shouldn't be reshuffled without reason), but
consider wrapping "Po cjelinama" and "Zadnji ispiti" in a collapsed `<details>` that
defaults open only once `Object.keys(store.seen).length > 0`, so a first visit leads with the
three mode cards and the one summary table, and the detail tables earn their place once
there's something in them.

**8. Keyboard hint text is incomplete.**
The in-quiz hint reads "tipke 1–4 · Enter" (quiz.html:327), but `ArrowRight`/`ArrowLeft` also
navigate (quiz.html:880-881) and aren't mentioned anywhere in the UI. Extend the hint string,
or move the full shortcut list into a small `title`/tooltip so the visible hint can stay short.

### Low priority / consider before acting

**9. 2.2 MB single-file payload, no loading state.**
`const DATA = {...}` is one inline JS statement holding all 1176 questions
(`build_quiz.py`'s `payload`), ~2.1 MB of the file's ~2.2 MB total. `JSON`-in-JS of this size
parses in well under a frame on any real device, so this isn't a runtime-performance problem
— but on a slow mobile connection the page is blank until the *entire* file has downloaded,
since nothing renders before the inline `<script>` at the bottom runs. This is almost
certainly the right tradeoff for a page whose whole value proposition is "one self-contained
file, works offline, one artifact URL" (see `NEXT_SESSION.md`'s publishing note) — flagging it
here only so it's a conscious tradeoff on record, not a silent one. No action recommended
unless real users report slow first loads.

**10. `.fig` figure background is hard-coded white in dark mode.**
`.fig{background:#fff; ...}` (quiz.html:139) doesn't follow `--card` in dark themes. This
looks like an oversight at first glance but is very likely deliberate: the images are raster
crops of scanned PDF pages (black ink on a white background baked into the PNG itself), so a
white *container* matches the image's own background seamlessly and avoids a mismatched
border where the crop isn't a perfect rectangle. Recommend leaving as-is. If it proves glary
in practice on a dark-mode phone at night, a small `filter:brightness(.92)` on `.fig` in dark
mode is a one-line, reversible experiment — but legibility of exam diagrams should win over
dark-mode purity if the two ever conflict, so test with a real user before changing it.

**11. `wrong`-queue review ignores the "izvor pitanja" pool filter.**
`start("wrong")` (quiz.html:432-434) pulls from `store.wrong` unconditionally, regardless of
`srcPool`. If someone answers a `priručnik` question wrong while "HRS + priručnik" is
selected, then switches the header dropdown back to "Samo HRS lista," that book question can
still surface in "Ponavljanje grešaka." Minor — the feature name ("questions you got wrong")
arguably justifies ignoring the pool filter — but worth a deliberate decision rather than
leaving it as an accident of how the two features happened to compose. No change proposed
without Glaukon's call on intended behaviour.

## Suggested rollout order

| Order | Items | Why this grouping |
|---|---|---|
| 1 | #1, #4 | Same mechanism (headings gain `tabindex`/id), same function (`show()`/markup only), highest a11y value |
| 2 | #2 | Isolated to the option-rendering loop in `render()`, no shared code with #1 |
| 3 | #3 | CSS-only, independent of the above |
| 4 | #5, #6, #8 | Small, independent, no shared code |
| 5 | #7 | Cosmetic/IA reorder — do last since it's the most subjective and easiest to bikeshed |
| — | #9, #10, #11 | Backlog / decide-only, not fixes |

None of these touch `questions.json`, `DATA`, the build pipeline, or answer content — the
usual `rebuild.py` / `strict.py` / `check_notes.py` verification gates are irrelevant here.
The only check that matters after any of these lands: open `quiz/quiz.html` (or the published
artifact) and click through home → practice → answer a question → finish, once with a
keyboard only and once with a screen reader, to confirm focus actually lands where intended.
