# Restore book stem figures: skupina II

prio:       P2
cluster:    book-figures
files:      quiz/build/book_overrides.json, quiz/build/book_figures.py, quiz/build/figs_book/
blocked-by:

**Why.** 12 of the 14 SKUPINA II — tehnički questions on 0031's candidate list are
missing a stem picture, and a prior attempt already fixed all 12 correctly, but the whole
item was stashed as failed because 2 *other* candidates on the same list turned out not to
be fixable under this item's rules. Recover, don't redo: `git stash list` for the entry
tagged `queue P2-0033: fail`, `git stash show -p <that stash>` to confirm it still applies
cleanly to `book_overrides.json`/`fig_windows.json`, then `git stash apply` it (not `pop`,
so a bad apply can be backed out) and `git stash drop` once verified. The stash's own
untracked `queue/reports/P2-0033.md` (3rd stash parent — `git show <stash>^3:queue/reports/P2-0033.md`)
has the full account: 7 fresh `figure` windows plus 5 amended merged-block entries
(`bk-teh-2-02/04/06/07/08/09/12/15/16/17/19/58`), each hand-corrected against
`fig_windows.json`'s raw proposals (which the report shows are wrong whenever real options
are short numeric/unit strings — a `find_next_marker()` bug in `fig_audit.py`, tracked
separately as [[P2-0043]] rather than fixed here) and each opened by eye.

The other 2 of the original 14, `bk-teh-2-28` and `bk-teh-2-30`, are confirmed (same
report) to have no figure at all — false positives of the gap heuristic. They are not this
item's problem: closing them out of `fig_audit.py`'s outstanding list is [[P2-0043]]. The
15th id some 0031 counts implied, `bk-teh-2-03`, is a mis-parsed figure-*options* question
that can't take a plain crop window under this item's own "Avoid" — that's [[P2-0042]].

**Done when.** The 12 ids above have a `figure` window in `book_overrides.json`, a PNG in
`figs_book/`, and an entry in `figs_book_index.json`, matching the stash's own crops (open
each one — the report's claim that they're correct is not a substitute for looking);
`rebuild.py` reports 1176 questions and `strict.py` is at or above 96.3% (the stash's own
recorded result, up from 0031's 95.4% baseline); the recovered stash is dropped once its
contents are staged.

**Avoid.** `bk-teh-2-20` and `bk-teh-2-46` already have figures and are figure-*options*
questions — leave both alone. `figure_is_options` is false for everything you add here.
Never touch an answer. Keep the red neutralisation in `figures2.postprocess`. Do not
attempt `bk-teh-2-03`, `-28`, or `-30` here — they're filed separately on purpose.
