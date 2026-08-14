# Publishing the quiz to GitHub Pages

The quiz is distributed as a **live GitHub Pages link**, not as clone-and-build. This
document is the repeatable procedure for producing and publishing that link. Follow it
exactly rather than improvising from memory each time — see `queue/todo/P2-0058-*.md` for
why this needed writing down.

## Why this can't be a GitHub Actions build

`quiz/quiz.html`, `quiz/questions.json`, and `quiz/images/` are gitignored on every branch
(see `.gitignore`'s own comment: it's what keeps parallel branches mergeable — nobody edits
generated files, so nothing to conflict). Normally that would be exactly the kind of thing
CI rebuilds on every push. **It can't be, here**: `docs/` — the source PDFs the build reads
(HRS's exam banks, the priručnik, CEPT/ERC references) — is deliberately excluded from the
public repo (`queue/todo/P1-0055-*.md`, `queue/todo/P1-0056-*.md`) because it's copyrighted
material credited but not redistributed. A GitHub Actions workflow only has what's in the
pushed repo to work with, and `docs/` will never be part of that. **Do not add a CI/Actions
workflow that runs `rebuild.py`** — it will fail (or worse, silently build from stale/partial
inputs) because its `docs/` input doesn't exist in the repo it's checked out in.

The build must happen **locally**, where the real `docs/` still lives on disk (see
`.gitignore`'s `docs/` entry and `quiz/build/rebuild.py`'s `SOURCES` dict, which reads
`docs/*.pdf`). Only the *output* — `quiz/quiz.html`, `quiz/questions.json`,
`quiz/images/` — gets published, by committing it to a separate branch that GitHub Pages
serves directly.

## 1. Rebuild locally

Requires the local, untracked `docs/` directory (the source PDFs) to be present — it is not
and will not be in the public repo.

```bash
python quiz/build/rebuild.py
```

This regenerates `quiz/questions.json`, `quiz/quiz.html`, and `quiz/images/*.png` in place
(it derives its output directory from its own file location, `quiz/build/`'s parent — not
from cwd — so run it from anywhere in the repo). It aborts rather than ship an unanswerable
question; a clean run ends with `1176` questions and no integrity failures. Do not publish
output from a run that aborted.

Optional but recommended before publishing — these must not regress:

```bash
python quiz/build/strict.py
python quiz/build/check_notes.py
```

## 2. Publish the build output to `gh-pages`

**Chosen approach: a standalone orphan branch named `gh-pages`, committed with `git add -f`
for the three gitignored paths.** Why this over alternatives:

- A *worktree* (`git worktree add`) would work too, but an orphan branch is simpler to
  document as a linear sequence of commands and doesn't require a second on-disk checkout
  to keep track of.
- Publishing from `main` directly (removing `quiz/` from `.gitignore`) was rejected — that's
  exactly the mergeable-branches problem `.gitignore`'s own comment exists to prevent. The
  generated files must stay gitignored on `main` and every work branch; `gh-pages` is the
  one place they're intentionally tracked.
- An orphan branch (`git checkout --orphan`) is used, not a branch forked from `main`,
  because `gh-pages` should hold *only* the built site — it has no reason to carry this
  repo's full history (including `docs/`'s pre-P1-0056 history, once that rewrite lands).

### One-time setup: create the `gh-pages` branch

Run this once, the first time the site is published. `origin` now points at
`glaukon-ariston/ham-radio-license-quiz` (created and wired up in P2-0061) — everything below
runs against that remote.

```bash
git checkout --orphan gh-pages
git rm -rf --cached .
python quiz/build/rebuild.py
git add -f quiz/quiz.html quiz/questions.json quiz/images/
git commit -m "Publish quiz build to gh-pages"
git push -u origin gh-pages
git checkout queue-drain
```

`git add -f` is required because all three paths are gitignored (by design, so they don't
conflict on `main`/work branches) — `-f` overrides the ignore for this one commit, on this
one branch, deliberately.

### Every subsequent publish (after any content change)

Re-run the same two commands — rebuild, then commit the output — on the `gh-pages` branch:

```bash
git checkout gh-pages
python quiz/build/rebuild.py
git add -f quiz/quiz.html quiz/questions.json quiz/images/
git commit -m "Rebuild: <what changed>"
git push
git checkout queue-drain
```

**`quiz/images/*.png` filenames are not content-hashed** — a changed figure can silently
reuse an old filename that's still cached by a browser or CDN. Always `git add -f
quiz/images/` in full on every publish (as above), never just the files that look new, so
stale images that `rebuild.py` removed (it prints `N stale removed` when it prunes
orphaned PNGs from `quiz/images/`) are actually removed from the branch too, and so nothing
that changed is skipped by assuming an image was already up to date.

## 3. GitHub repository setting — no longer a manual step

Pushing a branch literally named `gh-pages` (above) is enough on its own: GitHub auto-enables
Pages the moment that branch exists, sourced from `gh-pages` at `/ (root)` — confirmed via
`gh api repos/<owner>/<repo>/pages`, which reported `"source":{"branch":"gh-pages","path":"/"}`
immediately after the first push, with no `Settings → Pages` click needed. If GitHub ever
changes this default, the equivalent manual step is **Settings → Pages → Build and
deployment → Source: Deploy from a branch → Branch: `gh-pages`, folder: `/ (root)`.**

GitHub serves `quiz/quiz.html` at `https://<owner>.github.io/<repo>/quiz/quiz.html` (paths
are root-relative to the branch, and the built files live under `quiz/` even on `gh-pages` —
nothing moves them to the branch root). Confirm the served URL once the build status is
`built` (`gh api repos/<owner>/<repo>/pages --jq .status`) and use that as the link in
`README.md`'s **Try it** line.

## Summary: what to re-run after any content change

1. `python quiz/build/rebuild.py` (locally, with `docs/` present) — regenerates
   `quiz/questions.json`, `quiz/quiz.html`, `quiz/images/`.
2. On the `gh-pages` branch: `git add -f quiz/quiz.html quiz/questions.json quiz/images/`,
   commit, push. Always include the full `quiz/images/` tree, not just changed files —
   filenames aren't content-hashed, so a stale image that should have been removed only
   goes away if the whole directory is re-added.

No other step is needed — GitHub Pages serves whatever is currently on `gh-pages` with no
separate deploy action once the one-time source setting (step 3) is in place.
