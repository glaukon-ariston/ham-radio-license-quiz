# Rewrite git history to strip docs/ from all commits before any public push

prio:       P1
cluster:    public-release
files:      (repo-wide git history rewrite — no tracked source files are edited)
blocked-by: -

**Why.** `docs/` (the two Radiokomunikacije scans, Pasarić's book, ~130MB of copyrighted
material) is already committed in this repo's history. Untracking it going forward
(P1-0055) does not remove it from history — anyone who clones and runs `git show
<old-commit>:docs/Radiokomunikacije.pdf` can still extract every file. `git remote -v` is
currently empty — **this repo has never been pushed anywhere** — so this is the one window
to fix it without a disruptive force-push later. Must land before the first `git push` to a
public remote.

**Done when.** No commit reachable from `main` or `queue-drain` contains a blob under
`docs/`: `git log --all --oneline -- docs/` returns nothing, and
`git rev-list --objects --all | grep docs/` returns nothing. Both branches still exist
afterward with their non-`docs/` history intact. (Commit hashes will all change — expected
and fine, since nothing has been pushed yet.)

**Avoid.** Do not delete the local `docs/` working-tree directory — only git's history is in
scope. Do not add a remote or push anything — this stays entirely local.

**Method (decided 2026-08-13, Glaukon):** `git filter-repo --path docs --invert-paths`
(needs `pip install git-filter-repo` first). Preserves commit-by-commit history.
