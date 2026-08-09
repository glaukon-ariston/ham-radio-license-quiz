# Audit which book questions have a figure and propose crop windows

prio:       P1
cluster:    book-figures
files:      quiz/build/fig_audit.py, quiz/build/fig_windows.json, quiz/build/rebuild.py
blocked-by:

**Why.** Only 6 of the 720 book questions carry a `figure`, and all six are questions whose
*options* are pictures. Stem figures were never in scope, so ~83 questions render as bare
text — `"Sklop na slici je:"` with no slika. Two detectors agree on the scope and neither
is sufficient alone: 51 stems name a figure ("na slici", "prema shemi", "kao na skici"),
while 64 have a stem→options gap over 60 pt in `book_parsed2.json`; only 32 are in both.
The gap detector is the stronger one — it finds `bk-teh-5-11` ("Koliki je napon U.?"),
which never says "slici" at all. Without a shared audit, items 0032–0037 each re-derive
this, six times, by eye.

**Done when.** `python quiz/build/fig_audit.py` prints one row per suspect book question —
id, PDF page, gap in points, which detector fired, whether a figure already exists — and
writes proposed crop windows to `fig_windows.json` keyed by question id, each a
`[y0, y1]` pair derived from the stem baseline and the topmost option y. It exits nonzero
when a question that had a figure has lost it, so `rebuild.py` can call it as a gate.
Validate the proposer against ground truth before declaring it done: the 6 windows already
in `book_overrides.json` plus the one 0030 measures by hand. A proposal that misses those
by more than ~10 pt is not usable and the offset rule needs rethinking.

**Avoid.** Propose, do not apply — the windows land in `book_overrides.json` in 0032–0037,
after a human eye has seen the crop. Do not widen the gap threshold to catch stragglers;
a false positive costs a wasted crop, a threshold tuned to noise costs trust in the audit.
Clear `blocked-by: 0031` on items 0032–0037 as the last step.
