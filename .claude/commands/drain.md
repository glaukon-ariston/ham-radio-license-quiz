---
description: Drain one cluster from the work queue using worker and checker subagents
---

Drain one cluster from the queue. You are the orchestrator: you pick, dispatch, judge short
reports, and commit. **You do the work of none of it.**

The rule that makes this affordable: **never open an item body, a packet, a notes file, or
anything under `docs/`.** Every one of those is tens of thousands of tokens, and your context
is the budget the whole run spends — it is paid again on every remaining item. You pass
*paths* to subagents. They read; you don't.

## Setup, once per drain

```
git switch queue-drain 2>/dev/null || git switch -c queue-drain
```

Refuse to start if the tree is dirty — say so and stop.

## Per item

1. **Pick**: `python queue/pick.py`. If `item: none ready`, report the tally and stop.

2. **Work**: dispatch a `general-purpose` subagent, synchronously (`run_in_background:
   false`), with a prompt of roughly this shape and nothing more:

   > Read `queue/BRIEF.md` — it defines your job, the rules, and your report contract.
   > Your item is `<path from pick.py>`. Do it, verify, write
   > `queue/reports/<number>.md`, stage with `git add`, and return the six-line report.

3. **Judge the report.** `status: done` and `rebuild: 1176 ok` and `strict:` not regressed
   → go on. Anything else → **Recover** (below).

4. **Check**: first `git add -A`, so the checker sees the worker's *whole* footprint and not
   just what it remembered to stage — anything left unstaged would otherwise skip the check
   and be swept into the commit anyway. Then dispatch an `Explore` subagent, read-only by
   construction, so it cannot touch the work it is judging:

   > Read `queue/CHECK.md`. Your item is `<path>`. Check the staged diff
   > (`git diff --cached`). Do not read `queue/reports/`. Return the four-line verdict.

5. **Land** on `verdict: pass`:

   ```
   git mv queue/todo/<item>.md queue/done/
   git add -A && git commit
   ```

   Message: `<item title> (<number>)`, then one line from the worker's `notes:` if it said
   anything, then `Checked-by: checker agent`.

   On `fail` or `unverified` → **Recover**.

6. **Next**: repeat from 1. Always re-run `pick.py` rather than working down a remembered
   list — the queue may have changed, and a `P1` filed mid-run must be taken next. Ignore
   `cluster:` when ordering; it matters only for worktree reuse under parallel fan-out.

   Keep going until `pick.py` says nothing is ready, or the circuit breaker trips.

## Circuit breaker

**Two consecutive Recover events → stop the run.** Report both reasons and do not pick
another item.

One item failing is an item problem. Two in a row is usually a systematic one — a broken
build, a bad assumption in the brief, a missing dependency — and without this the run would
grind the entire queue into `queue/blocked/` and look busy while doing it.

## Recover

Never try to fix a worker's output yourself; that is how the orchestrator's context gets
dirty and how a bad edit gets rationalised into the corpus.

```
git stash push -u -m "queue <number>: <status or verdict>"
git mv queue/todo/<item>.md queue/blocked/
```

Append the one-line reason to `queue/blocked/<number>.why`, commit that move, and continue
to the next item. The work is recoverable from `git stash list`; nothing is lost and nothing
half-done reaches the next worker.

A `rebuild.py` abort is the safety net working — never route around it.

## Stop and report

A run ends when nothing is ready, or the circuit breaker trips.

Print one line per item — number, verdict, commit sha — plus what `pick.py` says is ready
next and why the run ended. Keep the running tally as you go rather than reconstructing it
at the end; re-reading your own history to write the summary is the one place this loop can
still get expensive. Under ten lines for a short run; for a long one, one line per item and
a two-line tail.

Do not merge `queue-drain` into `main`. That is Glaukon's call after he has read the diffs.
