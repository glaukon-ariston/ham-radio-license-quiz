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

**`git checkout gh-pages` deletes `quiz/build/` first — plan for that.** The one-time setup
above uses `git checkout --orphan gh-pages`, which *keeps* the working tree untouched, so
`rebuild.py` was still sitting on disk when it ran. Every later publish instead uses a plain
`git checkout gh-pages` — a normal branch switch — and `gh-pages`'s tree holds only
`quiz/quiz.html`, `quiz/questions.json`, and `quiz/images/`, so switching to it deletes
everything else that's tracked on your work branch but absent from `gh-pages`, including the
whole `quiz/build/` directory the build scripts live in. Restore just that one path with a
pathspec-limited checkout (which doesn't touch `gh-pages`'s own tracked files, so it can't
conflict with them) rather than switching branches again:

```bash
git checkout gh-pages
git checkout queue-drain -- quiz/build      # restore the scripts gh-pages doesn't track
python quiz/build/rebuild.py
git add -f quiz/quiz.html quiz/questions.json quiz/images/
git commit -m "Rebuild: <what changed>"
git push
git restore --staged quiz/build             # the scripts don't belong in this branch's commit
rm -rf quiz/build                           # ...or in its working tree, before switching back
git checkout queue-drain
```

Skipping the `restore --staged`/`rm -rf` cleanup risks two things: an accidental `git add -f
quiz/build` would commit the build scripts onto `gh-pages`, which is meant to hold only the
built site; and the final `git checkout queue-drain` will refuse to run ("untracked working
tree files would be overwritten by checkout") because those restored scripts are untracked
here and drift from `queue-drain`'s committed copies the moment `rebuild.py` touches its own
JSON caches (`quiz/build/notes_*.json`, `book_overrides.json`, etc. — normal, expected churn
from re-running extraction, not something to chase down or preserve).

**`quiz/images/*.png` filenames are not content-hashed** — a changed figure can silently
reuse an old filename that's still cached by a browser or CDN. Always `git add -f
quiz/images/` in full on every publish (as above), never just the files that look new, so
stale images that `rebuild.py` removed (it prints `N stale removed` when it prunes
orphaned PNGs from `quiz/images/`) are actually removed from the branch too, and so nothing
that changed is skipped by assuming an image was already up to date.

**If any `git checkout` in this file fails with `cannot stat '<path>': Permission denied`**
(commonly `.claude/`, if a running Claude Code session has it open), the branch switch can't
even stat the locked directory to reconcile it — retrying doesn't help if the lock is
held by a live process, not a transient sync lock. Exclude that one path from the checkout's
comparison instead of waiting for it to free up:

```bash
printf '/*\n!.claude/\n' > .git/info/sparse-checkout
git config core.sparseCheckout true
git checkout <branch>                       # now skips the locked path
git config core.sparseCheckout false
rm -f .git/info/sparse-checkout
```

This only tells checkout to leave that path alone — it doesn't change what's tracked or
committed, so it's safe to use for any of the checkouts above.

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

1. `git checkout gh-pages`, then `git checkout queue-drain -- quiz/build` to bring the scripts
   back (a plain `gh-pages` checkout deletes them — see above).
2. `python quiz/build/rebuild.py` (`docs/` must be present) — regenerates
   `quiz/questions.json`, `quiz/quiz.html`, `quiz/images/`.
3. `git add -f quiz/quiz.html quiz/questions.json quiz/images/`, commit, push. Always include
   the full `quiz/images/` tree, not just changed files — filenames aren't content-hashed, so
   a stale image that should have been removed only goes away if the whole directory is
   re-added.
4. `git restore --staged quiz/build && rm -rf quiz/build`, then `git checkout queue-drain`.

No other step is needed — GitHub Pages serves whatever is currently on `gh-pages` with no
separate deploy action once the one-time source setting (§3, "GitHub repository setting"
above) is in place.
