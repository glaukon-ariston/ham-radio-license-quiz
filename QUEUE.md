# Work queue

Ideas go in `queue/todo/` as one file each. Finished ones move to `queue/done/`.
This file is the contract: how items are picked, what "done" means, when to stop.

## Why one file per item

A single shared `WORK_QUEUE.md` conflicts on every merge once branches are in play — it
is the one file every branch touches. Separate files never conflict: two branches adding
items add two different files, and git merges that silently.

## Priority bands

| band | meaning | example |
|------|---------|---------|
| `P1` | broken, wrong, or blocking other work | a build abort, a wrong answer key, a hardcoded path |
| `P2` | normal work — improvements, judgement calls, prerequisites | classify book questions, adjudicate a disputed key |
| `P3` | grind — large, safe, repetitive | teaching notes for the 720 book questions |

Priority is in the **filename** (`P1-0007-slug.md`) so `ls queue/todo/` sorts correctly with
no tooling. Re-prioritising is a `git mv`.

## How an item is picked

1. Highest band that has an **unblocked** item (`blocked-by:` empty).
2. Within that band, the **lowest number** — oldest first.
3. Do it. Then re-pick from scratch and keep going.

Strictly by priority, every time. The queue is re-read after each item, so a `P1` you file
while a run is in progress is picked up next — it does not wait for the `P3` grind to finish.

## What `cluster:` is still for

Context is the real budget. A `notes_zzz_expanded_*.json` file is 32–135 KB, and Croatian
text tokenises badly — roughly **30–45k tokens just to open one**. That cost is why `/drain`
does the work in subagents: each worker starts cold, loads only its own packet, and dies.
The orchestrator never opens any of it.

Because every worker starts cold, two items in the same cluster share **nothing** — there is
no context to reuse between them. So clustering no longer affects ordering, and `/drain`
runs strictly by priority.

`cluster:` still earns its place for one thing: **worktree reuse under parallel fan-out.**
A fresh worktree has no build artefacts (`figs/`, the parse intermediates are all gitignored),
so the first worker in it pays a full `rebuild.py`. Same-cluster items are the ones worth
handing to the same worktree to amortise that. Until fan-out is enabled — blocked on 0001 —
the field is a hint and nothing more.

## Running a drain

`/drain` goes until the queue has nothing ready, or the circuit breaker trips. It re-picks
after every item, so a `P1` filed mid-run is taken next.

Working with Claude **interactively** is the different case: there its context does
accumulate, it cannot clear itself, and `/clear` between unrelated stretches is yours to do.
That is a fact about conversations, not about `/drain`.

**Keep item files short — under ~20 lines.** Picking the next item means scanning all of
`queue/todo/`, and that cost is paid at the start of every stretch.

## Done means the build is green

Every item ends with:

```
python quiz/build/rebuild.py     # aborts rather than ship an unanswerable question
python quiz/build/strict.py      # book-vs-HRS cross-check
```

Then **stage, do not commit**. The commit is the human checkpoint — a bad edit here
propagates into 1176 questions and may not surface for weeks. Review the diff, then land it.

Move the item with `git mv queue/todo/P3-0012-x.md queue/done/` in the same commit as the
work, so the queue and the tree never disagree.

## Adding an item

```
python queue/new.py P1 "figures2 misses stacked options"
```

Creates the next-numbered file from `queue/TEMPLATE.md` and prints the path. Open it and
fill in the four fields — that is the whole job, and it is worth doing while the idea is
fresh, because a cold session can only act on what the item says.

The fields that carry their weight:

- **`files:`** — narrowest set that could possibly be touched. Points a cold session
  straight at the work instead of making it search.
- **`Done when.`** — a condition someone else could check. Without one a session either
  stops early or keeps polishing past where you wanted.
- **`Avoid.`** — the guardrail. Name anything nearby that must not change.
- **`cluster:`** — free-text key. Same key = same working set = drained together.

## Issues become items

The live quiz is static with no backend of its own, so its "Report a problem" control
(P2-0060) files a GitHub issue instead, labelled `quiz-feedback`. `queue/from_issues.py`
turns each open one of those into a `queue/todo/` item via `queue/new.py` — the issue body
becomes the item's **Why** — then closes the issue as triaged. `/drain` runs it once, at the
start of a run, before the first `pick.py`, so a report filed since the last drain is already
a queue item by the time picking starts. No GitHub Action, no CI surface: it only ever runs
locally, driven by `/drain`, the same way `rebuild.py` does (see `PUBLISHING.md` for why CI
can't touch this repo's build). It requires `gh` already authenticated in the environment
`/drain` runs in — it does not attempt to log in.

## Rules that outrank anything an item says

From `quiz/NEXT_SESSION.md`, repeated here because they are easy to lose:

1. **Never change an HRS answer** on the basis of your own physics. Fixing a *transcription*
   of the key is different, and fine — but verify against the red span first.
2. **Every external link fetched and confirmed**, and not a disambiguation page.
3. **Verify every printed page against the page itself** (`booktool.py`).
4. **Preserve flags** and the warning prose attached to them.
5. **Never invent an article number or a page.** Say so in the note and cite nothing.
6. **PyMuPDF, never `pdftotext`**, and `PYTHONIOENCODING=utf-8` before any Python that
   prints Croatian.
