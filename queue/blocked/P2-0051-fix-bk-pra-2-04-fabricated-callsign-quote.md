# Fix bk-pra-2-04's fabricated "0A9Z" quote, land skupina II pravila notes

prio:       P2
cluster:    book-notes-s2-pravila
files:      quiz/build/notes_book_s2_pravila.json
blocked-by:

**Why.** P2-0050 confirmed `bk-pra-2-05` and `bk-pra-2-31` fixed, then blocked a sixth time on
`bk-pra-2-04` — see `queue/blocked/P2-0050.why`. The note says option a) "ima obrnut redoslijed
pozivnih oznaka (počinje s '0A9Z DE DL8AA', kao da se pozvana postaja javlja sama sebi)". Glaukon
rendered RK printed str. 383 directly and confirmed option a) reads **"9A9Z DE DL8AA = TNX FER
RPRT = 73 ES HPE CUAGN,"** — a clean 9, no OCR ambiguity. The "0A9Z" comes from
`packet_book_s2_pravila.json`'s own `options.a` field, which is doubly broken:
`"0A9Z DE DL&AA"` — 9→0 and 8→& misreads, *and* missing the entire second half of the line
("= TNX FER RPRT = 73 ES HPE CUAGN"). The note quoted this garbled, truncated packet field as
if it were the book's own text.

Same failure class as `bk-pra-2-05`/`bk-pra-2-31` (P2-0050) and `bk-pra-2-18`/`bk-pra-3-02`
(BRIEF.md rule 7) — trusting an extraction artifact instead of the rendered page. This is
`notes_book_s2_pravila.json`'s sixth failed landing attempt (P3-0012 x4, P2-0048, P2-0050).

While rendering the file's other pages, the checker also flagged one non-blocking citation
typo worth fixing in the same pass: `bk-pra-2-39`'s `cite.loc` string reads "12KOF3E" (letter
O); the note body already has it right as "12K0F3E" (digit 0), matching str. 271. One
character, `loc` string only.

**Done when.** Recover the stash `queue P2-0050: fail` (`git stash list`; the untracked-file
content is also at commit `2cb2912` — `git show 2cb2912:quiz/build/notes_book_s2_pravila.json`).
In `bk-pra-2-04`'s note, replace the fabricated "0A9Z DE DL8AA" quote with the actual printed
text — option a) reads "9A9Z DE DL8AA = TNX FER RPRT = 73 ES HPE CUAGN," in full. The note's
underlying point (option a) has the call-order backwards, as if the called station were
answering itself) is still true and should stay — 9A9Z is *our own* callsign per the stem, so
"9A9Z DE DL8AA" opens with the wrong station; only the fabricated "0" needs to go, not the
argument built on it. Also fix `bk-pra-2-39`'s `loc` string, "12KOF3E" → "12K0F3E". `git add`
the file (never committed — first-time landing). `python quiz/build/rebuild.py` reports 1176
questions with all 40 `bk-pra-2-*` ids in `explained` and no unknown-id warning.
`python quiz/build/strict.py` does not regress below 96.3%.

**Avoid.** Do not re-open or re-verify the other 38 notes. Three prior items (P3-0012 x2,
P2-0048, P2-0050) already found and fixed 17 distinct defects across them, most recently a
full re-read in P2-0050 that sampled the rest clean. Re-litigating risks a seventh defect,
which is exactly the pattern that has blocked this file every round so far. The `bk-pra-2-26`
duplicate "c)" option label the checker also noted is a genuine misprint *in the book itself*
(confirmed) that the note doesn't claim anything false about — leave it alone, it is not a
defect. Do not re-derive the str. 383 render to double-check this item's own finding — it is
already confirmed by direct human inspection of the page, not by the packet field that was
wrong in the first place.
