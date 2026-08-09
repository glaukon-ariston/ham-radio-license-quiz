# Add balanced and vivid color theme options

prio:       P2
cluster:    quiz-app-ui
files:      quiz/build/build_quiz.py
blocked-by:

**Why.** Glaukon finds the current look "quite gray and dull." The app only ships
one palette pair — a muted teal accent (`--accent:#0B5563`/`#38BEC9`) that
switches light/dark via `prefers-color-scheme`, with matching `:root[data-theme=
"light"/"dark"]` blocks already defined at build_quiz.py:23-44 but nothing in
the page currently sets `data-theme` (no visible toggle control), so those
blocks are presently dead weight. Glaukon wants two additional colour options
alongside the existing one: one with a **balanced** palette, one with **vivid**
colours.

**Done when.** The page offers at least three selectable colour themes (current
muted one, a new balanced one, a new vivid one), each with both a light and
dark variant covering every CSS var in the `:root` block (--paper, --card,
--ink, --muted, --line, --accent, --accent-soft, --good, --bad, --good-soft,
--bad-soft, --warn, --warn-soft, --shadow, --fx-bg). There is a visible control
to switch between the three, the choice persists (e.g. via localStorage) across
reloads, and it composes with the existing light/dark preference rather than
replacing it. Verify by opening the built quiz page, cycling through all three
themes in both light and dark system settings, and confirming contrast stays
legible (options, correct/incorrect states, the pass-line meter) in every
combination.

**Avoid.** Don't regress the existing muted palette — it stays as the default/
first option. Don't hardcode colours anywhere outside the `:root` variable
blocks; every themed element already reads from `var(--*)`, so new palettes
should only need new variable sets. Check contrast carefully for the vivid
palette especially — "vivid" must not come at the cost of legibility for
option text, the why-box, or the good/bad answer states.
