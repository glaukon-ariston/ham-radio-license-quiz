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
3. Then drain that item's whole **`cluster:`**, and **stop**.

Priority beats clustering; clustering is only the tie-breaker inside a band. A new `P1`
therefore jumps ahead of a half-drained `P3` cluster, which is the point of having bands.

## Why "drain a cluster, then stop"

Context is the real budget. Items sharing a `cluster:` share their working set — the same
files, the same reference material — so doing them back to back reuses an expensive load.
A `notes_zzz_expanded_*.json` file is 32–135 KB, and Croatian text tokenises badly: roughly
**30–45k tokens just to open one**. Reloading that per item is the single largest avoidable
cost in this project.

Crossing a cluster boundary means that saving is gone anyway — so that is the cheapest
moment to stop, throw the context away, and start the next stretch cold. Carrying a finished
cluster's transcript into unrelated work pays for it on every later turn and buys nothing.

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
