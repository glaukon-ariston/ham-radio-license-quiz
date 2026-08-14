# Animate the Vodopad theme into full rave mode

prio:       P2
cluster:    quiz-app-ui
files:      quiz/build/build_quiz.py
blocked-by:

**Why.** P2-0059 gave the quiz a `waterfall` theme ("Vodopad", SDR panadapter-styled) but
deliberately shipped it static — that item's own **Avoid** said "don't animate... this page is
used during timed practice exams." Glaukon has since reversed that call: he wants Vodopad
pushed into a large animated background plus vivid, animated micro-interactions, visible
everywhere including while a question is on screen, not just on idle/start screens. This
supersedes P2-0059's "keep it static" instruction for this theme only — light and dark stay
exactly as static as before.

**Done when.** All of the below, in `quiz/build/build_quiz.py` only, waterfall-scoped so light
and dark stay byte-identical to today:

1. A fixed, full-viewport animated layer (`#fxbg`, a plain div with 1-2 child divs, inserted
   right before `<header class="bar">`) driven by CSS `@keyframes` on `transform`/`filter`/
   `opacity` only (no canvas, no SVG SMIL — both need hand-built start/stop/visibility/
   reduced-motion lifecycle wiring that a JS-free CSS approach gets for free from the existing
   `data-theme` selector and `@media(prefers-reduced-motion)`). Content: slow-drifting radial
   gradients in the existing `--fx-gradient` hues (~45-60s cycle) plus a scanline band
   (~6-8s) plus a `filter:hue-rotate()` cycle (~24s) on the layer itself, capped at an overall
   `opacity` around .5-.6. `z-index:-1`, `pointer-events:none`; requires a waterfall-scoped
   `body{background:transparent}` override (the existing unscoped `body{background:var(--paper)}`
   is opaque and would otherwise occlude it regardless of z-index) — check this doesn't collide
   with the file's only two existing z-indices (`header.bar`=20, `.confirm-mask`=30).
2. Because `--card`/`--paper` are fully opaque today, the animation would otherwise be
   invisible behind every question card during actual answering — the case that matters most.
   Add a new waterfall-only token, e.g. `--card-glass: color-mix(in srgb, var(--card) 82%,
   transparent)`, and give `.qcard`, `.opt`, `.mode`, `.stat`, `.confirm-box` a waterfall-scoped
   `background:var(--card-glass); backdrop-filter:blur(10-12px)` (mirrors the technique
   `header.bar` already uses at its own background). Do **not** touch `--card` itself (small
   controls — `.themesel`, `.btn`, `.report-select` — read it too and shouldn't go glassy), and
   do **not** apply glass to the state-colored variants (`.opt.sel/.ok/.no`, `.verdict.ok/.no`,
   `.why`/`.why.warn`/`.why.check`) — those must stay the solid, already-WCAG-checked colors
   P2-0059 verified, since post-answer feedback needs maximum legibility.
3. Re-verify WCAG contrast for the new glass surfaces — P2-0059's opaque-card numbers no
   longer apply. Write (or adapt P2-0059's, if you can find it referenced in
   `queue/reports/0059.md` — it wasn't committed as a standalone script) a relative-luminance
   contrast check: for each of the 5 `--fx-gradient` hues plus `--fx-bg`, compute that hue at
   the animation's capped opacity blended with `--card-glass`, and confirm `--ink`/`--muted`
   still hit ≥4.5:1 / ≥3:1 against every resulting composite. Tune `--card-glass` alpha /
   `#fxbg` opacity until the worst single hue clears — this is a pessimistic bound (real
   `backdrop-filter` blur spatially averages the backdrop, so the browser's true worst case
   will be better), which is fine, it just means don't over-tune against it.
4. Vividness additions, each a *new* waterfall-scoped rule layered after the rule it extends
   (never edit an existing shared rule, even where the edit would be visually inert in
   light/dark — matches the file's own existing `var(--x, fallback)` convention at
   `header.bar::after`/`.meter i`): animate the existing header hairline
   (`background-size:200% 100%` + a slow linear sweep); animate the meter's neutral fill the
   same way (leave `.meter i.ok`/`.meter i.no` solid, untouched — pass/fail must never depend
   on the gradient, in every theme); a one-shot glow pulse on `.opt.ok`/`.opt.no` firing off
   the JS's existing class toggles (no JS change needed there); hover glows on `.mode`/`.opt`/
   `.btn`; a slow "breathing" opacity pulse on a `.qcard::before` glow overlay (the one visible
   continuously during actual question-answering).
5. `@media (prefers-reduced-motion:reduce){:root[data-theme="waterfall"] #fxbg{opacity:0}}`
   added right after the existing global reduced-motion rule — must fully stop all motion, not
   just slow it, and land on a clean static look rather than an arbitrary frozen frame.
6. Update the stale explanatory comments at the current `header.bar::after` and `.meter i`
   rules — they say "Static, no animation... unaffected by prefers-reduced-motion since
   nothing here transitions" and "no motion was added anywhere"; both claims become false.
7. `python quiz/build/rebuild.py` succeeds (1176 questions, no integrity failures) and
   `python quiz/build/strict.py` shows no new disagreements. Open the built `quiz/quiz.html`,
   switch to Vodopad, and confirm by eye (chrome-devtools MCP is configured in this repo's
   `.mcp.json` if your session has it available — headless, isolated Chrome; use
   `navigate_page`/`take_screenshot`/`evaluate_script` to drive it) that: the background is
   visibly animating on the start screen AND behind an open question card; text stays legible
   over the animated glass card at a phone-width viewport (390px) as well as desktop; toggling
   `prefers-reduced-motion` (via `emulate`) freezes it completely — two screenshots ~1-2s apart
   come out pixel-identical; light and dark are visually unchanged. If your session has no
   browser/screenshot tool, say so explicitly in the report (as P2-0059's report did) rather
   than claiming visual verification you didn't perform, and lean harder on the analytical
   contrast check and a careful read of the generated CSS/JS instead.

**Avoid.** Don't touch light or dark — every new rule must be scoped under
`:root[data-theme="waterfall"]` or a class/attribute combination that only matches there;
nothing shared should change even in a way that's inert elsewhere. Don't add
`requestAnimationFrame`/canvas — this file has none today and a pure-CSS approach avoids
needing hand-built start/stop/visibility-pause/reduced-motion JS lifecycle code. Don't touch
`show()`, the 4-section SPA architecture, `DATA`/the question payload, or the `#themeSel`
change-listener's logic — this item is CSS/cosmetic plus at most a small defensive
Page-Visibility-pause JS snippet, nothing structural. Don't widen `--card-glass` to controls
outside the five listed selectors. Don't hand-edit `quiz/quiz.html` — it's generated by
`rebuild.py`/`build_quiz.py`. Keep all animation cycles in the tens-of-seconds range — no hard
flicker (WCAG 2.3.1 territory) — "full rave" means vivid and continuously moving, not strobing.
`.fig` has a pre-existing hardcoded `background:#fff` regardless of theme (a white box against
the near-black waterfall palette) — out of scope for this item, don't fix it, but don't be
surprised by it when screenshotting the question card.
