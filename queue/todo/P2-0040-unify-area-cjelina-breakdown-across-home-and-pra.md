# Unify area/cjelina breakdown across home and practice picker for all three sections

prio:       P2
cluster:    quiz-app-ui
files:      quiz/build/build_quiz.py
blocked-by:

**Why.** Glaukon wants clicking "Vježba — odaberi područje" (the `#picker`
screen, built by `buildPicker()` at build_quiz.py:546-563) to land somewhere
he can either take random questions from a whole area or drill into a
cjelina — today that drill-down only exists on the home page's "Tehnički dio
po cjelinama" table (`subTable`, home() at build_quiz.py:517-530), and
`buildPicker()` only offers whole-section buttons, no cjelina rows. He also
wants the home page to show the same per-cjelina breakdown for Propisi and
Pravila i postupci, not just Tehnički.

**Scope constraint — read before starting.** `q.sub` is null for every
propisi/pravila question; only the 282 tehnicki questions have a cjelina
classification. This was a deliberate decision, not an oversight — see
`quiz/build/book_subsections.json:8`: "the propisi and pravila banks carry no
chapter headings in the HRS source... there is no existing vocabulary to draw
from, and inventing one would be exactly the misfiling the item warns
against." Do not invent cjelina names for propisi/pravila as part of this
item. For those two sections the breakdown correctly degrades to a single
"whole area" row/entry — that's a real result of the data, not a bug to work
around.

**Done when.**

1. The picker screen (or wherever "Vježba — odaberi područje" now lands)
   offers, per section, both a "whole area" option and — for tehnicki only —
   one row per cjelina with its own seen/success stats, reusing the stats
   logic already in home()'s `subTable` build (build_quiz.py:517-528) rather
   than duplicating it.
2. Propisi and Pravila i postupci each show as a single whole-area entry in
   that same breakdown (consistent with point 1's constraint), instead of
   being absent from any per-area breakdown beyond the existing top-level
   `secTable`.
3. The existing home-page `subTable` either becomes this same breakdown (if
   folded into the picker) or is left consistent with it — no two diverging
   implementations of "cjelina breakdown" in the file.

**Avoid.** Don't invent a propisi/pravila subsection taxonomy (see scope
constraint above) — that's a separate, deliberately-not-yet-done content task,
not a UI task. Don't regress the existing "Sve iz HRS lista" / "Dodatna iz
priručnika" picker buttons (build_quiz.py:560-562). Coordinate with item 0039
(breadcrumb links) since both touch `start("practice", {filter})` entry
points into the same sections/cjeline — either order is fine, but keep the
filter-building logic in one place if both land close together.
