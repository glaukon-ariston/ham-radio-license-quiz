# Make rebuild.py write relative to its own checkout

prio:       P1
cluster:    build-pipeline
files:      quiz/build/rebuild.py:13, quiz/build/build_quiz.py
blocked-by:

**Why.** `DST` is the absolute Drive path `g:/My Drive/.../quiz`, so a rebuild run from a
worktree writes its `questions.json` and `quiz.html` back into the main tree — silently
clobbering it and attributing the result to the wrong branch. This blocks running builds
in parallel worktrees at all.

**Done when.** `rebuild.py` run from `C:\dev\ham-worktrees\<any>` writes into *that*
worktree, `git status` is clean in both trees afterwards, and a run from the main tree
still produces the same 1176-question output as today.

**Avoid.** `build_quiz.py` resolves its own paths — check it takes the same treatment
rather than assuming. Do not make the source PDF paths relative; `docs/` is shared.
