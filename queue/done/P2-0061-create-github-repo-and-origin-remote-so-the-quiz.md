# Create GitHub repo and origin remote so the quiz feedback button works

prio:       P2
cluster:    publishing
files:      (none in this repo — GitHub-side setup; quiz/build/build_quiz.py reruns after)
blocked-by: Glaukon — repo creation is a decision for him, not a side effect of drain (see PUBLISHING.md)

**Why.** `git remote -v` is empty (no `origin`), so `build_quiz.py`'s `repo_slug()` bakes
`REPO = ""` into `quiz.html` and the P2-0060 "Prijavi problem" (report a problem) button hides
itself rather than link to a broken URL. Suggested repo name: **`ham-radio-license-quiz`**
(matches this working directory's own name, descriptive of what's published — free to rename
before creating it).

**Done when.** A GitHub repo exists, `git remote add origin git@github.com:<owner>/<repo>.git`
is set on this local repo, a label named exactly `quiz-feedback` exists on that repo (GitHub
silently drops unknown label names from the issue-URL `labels=` param otherwise), and
`python quiz/build/build_quiz.py` has been rerun so the regenerated `quiz.html` bakes in the
real `REPO` and shows `#reportBtn`. Follow `PUBLISHING.md` for the rest of the one-time
`gh-pages` setup if that hasn't happened yet either.

**Avoid.** Do not run `docs/`-reading `rebuild.py` output through any CI/Actions workflow —
`PUBLISHING.md` explains why (`docs/` is deliberately not in the public repo). Do not add a
`gh auth login` flow. Creating the repo itself and pushing are the human-in-the-loop steps —
say what you're about to do and confirm before running `gh repo create` or `git push`.
