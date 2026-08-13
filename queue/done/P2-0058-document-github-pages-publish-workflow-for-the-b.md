# Document GitHub Pages publish workflow for the built quiz

prio:       P2
cluster:    public-release
files:      PUBLISHING.md (new)
blocked-by:

**Why.** `quiz/quiz.html`, `quiz/questions.json`, and `quiz/images/` are gitignored on
purpose (`.gitignore`'s own comment: keeps parallel branches mergeable). Glaukon decided
(13 Aug 2026) the public-facing way to use the quiz is a live GitHub Pages link, not
clone-and-build. But CI can't build it — the source PDFs in `docs/` are being deliberately
excluded from the public repo (P1-0055/0056), so there's nothing for a GitHub Actions
rebuild to read. The build has to happen locally, where the real `docs/` still lives, and
only the *output* gets published. This needs to be written down as a repeatable procedure,
not done ad hoc from memory each time.

**Done when.** `PUBLISHING.md` exists at the repo root with concrete, copy-pasteable
commands covering:
1. Rebuild locally: `python quiz/build/rebuild.py` (requires the local, untracked `docs/`).
2. How the build output reaches a `gh-pages` branch given it's gitignored on every other
   branch — e.g. `git add -f quiz/quiz.html quiz/questions.json quiz/images/` when
   committing *on the `gh-pages` branch specifically* (an orphan branch that does not
   inherit history from `main`), or an equivalent documented approach. State whichever
   approach is chosen and why, don't leave it vague.
3. One-time GitHub repo setting: Pages source = `gh-pages` branch, root.
4. What to re-run and re-publish after any content change (same two commands, plus a note
   that `quiz/images/` must be republished in full each time since image filenames aren't
   content-hashed).

**Avoid.** Do not actually create a `gh-pages` branch, push anything, or touch GitHub repo
settings — there is no remote configured yet (`git remote -v` is empty) and creating one is
Glaukon's call, not this item's. This item only writes the procedure down. Do not propose
building in CI/GitHub Actions — the source PDFs won't be in the public repo, so a CI
rebuild has nothing to read; say so explicitly in the doc so a future reader doesn't
"helpfully" add a workflow that will fail. Don't touch `.gitignore` beyond what P1-0055
already does.
