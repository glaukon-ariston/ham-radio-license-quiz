# Add question-feedback reporting to the quiz

prio:       P2
cluster:    quiz-feedback
files:      quiz/quiz.html, queue/from_issues.py, .claude/commands/drain.md, QUEUE.md
blocked-by:

**Why.** A quiz taker who spots a wrong answer, a typo, or a bad citation has no way to
flag it from the live GitHub Pages quiz, and the quiz is static with no backend — the only
thing available to receive a report is something that already has a backend, which here
means GitHub itself.

**Done when.** Each question in quiz.html has a "Report a problem" control that opens a
small form (reason + free text) and opens a prefilled `github.com/<owner>/<repo>/issues/new`
URL (owner/repo read from `git remote get-url origin`, not hardcoded) with the question id,
current answer/citation, and the note, labelled `quiz-feedback`. `queue/from_issues.py` runs
`gh issue list --label quiz-feedback --state open`, and for each open issue creates one
`queue/todo/` item via `queue/new.py` (issue body becomes the Why), then closes the issue as
triaged. `drain.md`'s "Setup, once per drain" step calls this script before the first
`pick.py`, so filed issues become queue items at the start of a drain with no GitHub Action.

**Avoid.** No CI workflow / GitHub Action for this — the point of the drain-time version is
zero new CI surface. Don't let the script write into `queue/todo/` directly; go through
`queue/new.py` so numbering stays unique across `todo/` and `done/`. `gh` must already be
authenticated in the environment that runs `/drain` — don't add a login flow.
