"""Drain open GitHub `quiz-feedback` issues into queue/todo/ items.

The live quiz has no backend of its own to receive a report — its "Report a problem"
control (P2-0060, quiz/build/build_quiz.py) opens a prefilled `github.com/<owner>/<repo>/
issues/new` URL instead, labelled `quiz-feedback`, since GitHub is the one thing already
available with a backend. This script is the other half: it turns each open issue with that
label into a queue item, so a report a quiz taker filed becomes work the next drain will pick
up, with no GitHub Action and no new CI surface.

    python queue/from_issues.py

Called once, at the start of a drain, from `.claude/commands/drain.md`'s "Setup, once per
drain" step, before the first `pick.py` — so issues filed since the last drain are already
queue items by the time picking starts.

Requires `gh` already authenticated in the environment this runs in; this script does not
attempt to log in (nor should it — see the item this implements).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
LABEL = "quiz-feedback"


def run(*args):
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        sys.exit(f"from_issues.py: `{args[0]}` not found — is it installed and on PATH?")
    if r.returncode:
        sys.exit(f"from_issues.py: `{' '.join(args)}` failed:\n{r.stdout}{r.stderr}")
    return r.stdout


def file_item(issue):
    """Create one queue/todo/ item for `issue` via queue/new.py — never write into
    queue/todo/ directly, so numbering stays unique across todo/ and done/ (see new.py's own
    docstring). Returns the repo-relative path new.py printed."""
    title = issue["title"].strip() or f"Quiz feedback #{issue['number']}"
    body = (issue.get("body") or "").strip() or "(issue filed with no body)"

    rel_path = run(sys.executable, str(HERE / "new.py"), "P2", title).strip()
    item_path = ROOT / rel_path
    text = item_path.read_text(encoding="utf-8")

    # cluster: one shared key for every issue-filed item, so a parallel fan-out can drain
    # them from the same worktree. files: left as a pointer rather than a guess — which
    # notes_*.json (or bank.json / quiz.html itself) is the right one depends on the question
    # id named in the issue body, and only a worker that reads the body can resolve that.
    text = re.sub(r"^cluster:( +).*$", r"cluster:\1quiz-feedback", text, count=1, flags=re.M)
    text = re.sub(
        r"^files:( +).*$",
        r"files:\1<identify from the question id in Why, below — "
        r"quiz/build/notes_*.json is the usual answer>",
        text, count=1, flags=re.M)
    text = text.replace(
        "**Why.** One or two sentences. What is wrong or missing, and what it costs. "
        "Not history.",
        f"**Why.** Filed from the live quiz via GitHub issue #{issue['number']}, "
        f"reproduced here unedited:\n\n{body}")
    item_path.write_text(text, encoding="utf-8")
    return rel_path


def main():
    out = run("gh", "issue", "list", "--label", LABEL, "--state", "open",
              "--json", "number,title,body")
    try:
        issues = json.loads(out or "[]")
    except json.JSONDecodeError:
        sys.exit(f"from_issues.py: couldn't parse `gh issue list` output:\n{out}")

    if not issues:
        print("--- from_issues: no open quiz-feedback issues")
        return

    for issue in issues:
        rel_path = file_item(issue)
        run("gh", "issue", "close", str(issue["number"]),
            "--comment", f"Triaged into `{rel_path}`.")
        print(f"--- from_issues: issue #{issue['number']} -> {rel_path}")


if __name__ == "__main__":
    main()
