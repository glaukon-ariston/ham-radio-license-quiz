# Untrack docs/ before public release

prio:       P1
cluster:    public-release
files:      .gitignore
blocked-by:

**Why.** `docs/` holds copyrighted source material that must not end up in a public repo:
two ~50MB scans of HRS's own *Radiokomunikacije* priručnik, and a 23MB out-of-print book
by a named external author (Božidar Pasarić, 9A2HL — *Radioamaterizam za mlade*, published
in the University of Zagreb's official textbook series, 2008), plus assorted HRS exam-bank
PDFs. Glaukon decided (13 Aug 2026) the public repo will list and credit every source but
not redistribute the files themselves. Right now only `emails/` is gitignored — `docs/` is
fully tracked (21 files, `git ls-files docs/`).

**Done when.** `.gitignore` gains a `docs/` entry (match the existing style/comment above
the `emails/` line at the bottom of the file). `git rm -r --cached docs/` has been run and
staged, so `git ls-files docs/` prints nothing. `ls docs/` still shows all 21 files present
on disk — nothing was deleted, only untracked.

**Avoid.** Do not delete anything from disk — `docs/` is still needed locally to run
`quiz/build/rebuild.py`. Do not touch any `quiz/build/*.py` script; they read `docs/` by
relative path and don't care whether git tracks it. **This item does not remove `docs/`
from existing git history** — the files are still recoverable from old commits after this
change. That's a separate, higher-stakes item (P1-0056); don't attempt a history rewrite
here.
