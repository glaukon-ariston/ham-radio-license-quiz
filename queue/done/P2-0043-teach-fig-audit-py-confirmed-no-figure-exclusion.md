# Teach fig_audit.py confirmed-no-figure exclusions

prio:       P2
cluster:    book-figures
files:      quiz/build/fig_audit.py
blocked-by:

**Why.** `fig_audit.py`'s GAP detector (stem→options y-distance > 60pt) throws false
positives on questions whose stem simply wraps 3–4 lines with no picture at all —
confirmed by eye for `bk-teh-2-28` and `bk-teh-2-30` (66.9pt and 76.8pt gaps, pure text on
both rendered pages, see `queue/reports/P2-0033.md`, recovered via `git stash list` under
`queue P2-0033: fail`). Today there is no way to mark a candidate id as "checked, no
figure exists" — it stays on the outstanding list forever and blocks every downstream
item's "Done when: fig_audit.py reports nothing outstanding" clause. This will recur for
skupina III–VI (0034–0037), not just II, since the heuristic is unchanged there.

**Done when.** `fig_audit.py` supports an explicit exclusion list (ids confirmed to have
no figure, with a one-line reason each) that suppresses them from the "outstanding" report
without touching `book_overrides.json`; `bk-teh-2-28` and `bk-teh-2-30` are in it;
`fig_audit.py`'s own regression gate (the check that a previously-applied figure hasn't
vanished) is unaffected; `rebuild.py` still reports 1176 questions.

**Avoid.** This is a suppression list, not a fix to the GAP/NAME heuristics themselves —
do not tune the 60pt threshold to make `-28`/`-30` pass "naturally"; that risks hiding a
real gap elsewhere the same way the item's own "Avoid" elsewhere warns against tuning to
noise. Every id added to the exclusion list must have been confirmed by eye against the
rendered PDF page, not assumed from the gap size alone.
