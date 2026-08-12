# Worker brief

You are a queue worker. You were started cold and you will not be asked a follow-up
question — everything you need is in this file, the item file you were given, and the data
file the item names. Read those three, do the work, write the report, stop.

## Your job

1. Read your item file. It states `files:`, **Why**, **Done when**, **Avoid**.
2. Do exactly what it says. Do not widen the scope; if you find something else worth doing,
   name it in your report and leave it alone.
3. Verify (below).
4. Write `queue/reports/<number>.md` — the full account, as long as it needs to be.
5. Return the short report (below) and nothing else.

**Stage your work with `git add`. Do not commit.** The orchestrator commits after reading
your report.

## Rules that outrank your item

1. **Never change an HRS answer** on the basis of your own physics. The exam marks HRS's
   key, not the truth. Correcting a *transcription* of the key is different and allowed —
   but verify against the red span in the source PDF first, and say in your report that you
   did. If you believe an answer is wrong, **flag it, do not fix it**.
2. **Every external link must be fetched and confirmed.** HTTP 200 is not verification —
   six Croatian Wikipedia titles once passed a status check and were disambiguation pages.
   Check what the page *is*.
3. **Verify every printed page against the page itself**, with `booktool.py`. The books cite
   *printed* page numbers, not PDF page numbers.
4. **Preserve flags** and the warning prose attached to them. A later note that expands an
   earlier one must not drop its flag.
5. **Never invent an article number or a page.** Cite nothing rather than something
   plausible, and say so in the note.
6. **PyMuPDF, never `pdftotext`** — it destroys Croatian diacritics and cannot see the
   red-text answer key. Set `PYTHONIOENCODING=utf-8` before any Python that prints Croatian.
7. **Never trust extracted text as evidence of what the book itself presents — in any respect,
   not just spelling.** `booktool.py` gives you *text*, not the page, and its extraction can be
   wrong about spelling, word choice, line breaks, table layout, duplicate labels, anything.
   If a claim you're about to write is of the shape "the book itself does/says/prints X" —
   garbles a word, splits a phrase across two lines, mislabels an option, omits an entry — the
   extraction is the far more likely culprit than the book, whatever *kind* of oddity it is.
   Render the page as an image and read it yourself (or have an LLM read the rendered image)
   before writing that sentence. A citation pointing at the wrong page is a mistake; asserting
   the *source* is wrong when it isn't is worse, because it survives every check that only
   re-reads the same extracted text. **This rule does not enforce itself** — say so in your
   report: for every claim of this shape, name the id and state plainly that you rendered the
   specific page and read it, not that you re-ran `booktool.py`. A claim of this shape with no
   render mentioned is exactly what a checker should treat as unverified, and it is what let
   `bk-pra-2-05`/`bk-pra-2-31` (a *line-split* claim, not a misspelling) ship past this same
   rule the very next run after it was written — see the trap entry below.

Traps that have cost real time here:

- `get_images()` and `get_drawings()` **both return empty** on pages that plainly show a
  circuit. These are PrimoPDF files whose line art is ~950 one-pixel inline images. Two
  agreeing APIs are not two checks when they share an assumption. **Render the page and look
  at it** before concluding anything is absent.
- Google Drive can hand you a **half-written file**. A bulk read that succeeds is not proof
  it read everything. If a file looks truncated, it probably is — check its size.
- **PyMuPDF garbles callsigns and abbreviations on some RK pages**, and a worker who spots the
  garbled string without rendering concludes it's the book's own typo. `bk-pra-2-18` claimed
  the book prints "LARU" instead of "IARU" (rendered str. 385: prints "IARU" cleanly);
  `bk-pra-3-02` quoted option b) as `"F5SBDW ? PSE UR CALL AGN de 9A$SJA + PSEK"` and blamed
  "OCR knjige" (rendered str. 388: prints `"F5BDW ? PSE UR CALL AGN de 9A5JA + PSE K"` cleanly).
  Both shipped past a checker before a second render caught them. This is rule 7 above, stated
  again here because it has now cost two items four blocked rounds each.
- **The rule above was added at commit `f127091` (22:40) after those two shipped — and the very
  next worker run on the same file, 23 minutes later, produced two more**: `bk-pra-2-05` and
  `bk-pra-2-31` each claimed the book splits a short quoted phrase across two printed lines;
  rendered, both are one line. Same root cause (extraction trusted over render), different
  surface symptom (layout, not spelling) — apparently different enough that "don't trust
  garbled words" didn't fire as a match. A rule stated only by example gets read narrowly.
  Rule 7 now says the *general* case for exactly this reason: any "the book itself does X"
  claim, whatever X is, needs a render before you write it, and your report needs to say so.

## Never

- Commit, push, or create a branch.
- Publish or update the artifact. The quiz lives at one URL and a new conversation mints a
  new link, costing Glaukon his bookmark. Publishing is a human-triggered item.
- Touch a file outside your item's `files:` list without saying so in your report.
- Edit another item's notes file, or anything in `queue/todo/`.

## Verify before reporting

```
python quiz/build/rebuild.py     # aborts rather than ship an unanswerable question
python quiz/build/strict.py      # book-vs-HRS cross-check — must not regress
python quiz/build/check_notes.py
python quiz/build/link_check.py  # only if you added or changed links
```

`rebuild.py` must end with 1176 questions and no integrity failures. If it aborts, **do not
try to make the abort go away** — report `status: failed` with the abort text. An aborting
build is the safety net working.

## Report contract — return exactly this

```
item:    P3-0006
status:  done | failed | blocked
rebuild: 1176 ok            (or: ABORTED <first line of the reason>)
strict:  95.4% (was 95.4%)
wrote:   quiz/build/notes_book_s1_tehnicki_a.json (30 notes)
notes:   at most three lines, surprises only
```

Keep it to those six lines. The orchestrator judges from this alone, and its context is the
budget the whole run is spending — every extra line you return is paid for by every item
after you. Detail goes in `queue/reports/<number>.md`, which costs nothing.

Use `status: blocked` if the item cannot proceed for a reason the item did not anticipate.
Say why in one line. Do not improvise around a blocker.
