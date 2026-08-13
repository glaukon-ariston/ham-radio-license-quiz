# Fix bk-pra-2-18 fabricated LARU book-typo claim, land skupina II pravila notes

prio:       P2
cluster:    book-notes-s2-pravila
files:      quiz/build/work/packet_book_s2_pravila.json, quiz/build/notes_book_s2_pravila.json

**Why.** P3-0012 (skupina II pravila, 40 notes) has been blocked four times. The three
originally-named citation defects and nine more found across two repair rounds are all fixed
and confirmed — see `queue/blocked/P3-0012.why` for the full history. It is blocked a fourth
time on one remaining defect in `bk-pra-2-18`: the note asserts the *book itself* prints
"LARU" instead of "IARU" ("i sâm tiskani udžbenik na više mjesta piše 'LARU' umjesto 'IARU'
... riječ je o osobitosti izvornika, a ne o slučajnoj pogrešci OCR-a"), citing str. 267 and
the exam question on str. 385 as evidence. This is false — rendered directly, str. 385
question 18 prints "Što znači kratica IARU?" cleanly, and the OCR-derived text the note relied
on is what garbled it, not the book. Confirmed independently by both the round-3 checker and
Glaukon. See the new rule 7 / trap in `queue/BRIEF.md` — this defect is the reason it exists.

**Done when.** Recover stash `queue P3-0012: fail (repair attempt 3)` (`git stash list`;
`git stash show -u <ref> --stat` to confirm it's the right one before applying). In
`bk-pra-2-18`'s note, remove the false "the book itself writes LARU" claim and the aside about
it being "osobitost izvornika, a ne pogreška OCR-a" — rewrite so the note simply answers what
IARU stands for (Međunarodni savez radioamatera / International Amateur Radio Union) without
asserting anything about a misspelling in the source. Keep the rest of the note (the
explanation of why the other three options are wrong) intact; it was never in dispute. Render
str. 385 and str. 267 yourself before writing the replacement — do not reuse the old citation
text as a starting point. `rebuild.py` reports 1176 questions, `explained` includes all 40 of
this packet's ids with no "unknown ids" warning for `bk-pra-2-*`, `strict.py` does not regress
below 96.3%.

**Avoid.** Don't re-open any of the other 39 notes in this file — they were verified clean
across three rounds and re-litigating them risks introducing a fifth defect. Don't just delete
the disputed sentence and leave a gap; the note must still fully answer the question. Rule 7 in
BRIEF.md applies here directly: verify by rendering, not by re-reading `booktool.py`'s text
output, which is the same extraction that caused this defect.

---

**Closed out, superseded (12 Aug 2026).** notes_book_s2_pravila.json landed via P2-0051
(round 9), which recovered this item's own stash lineage and fixed every remaining defect.
The checker for that round rendered all 26 cited pages and verified every quoted string
character-by-character across all 40 notes — the file is in the committed corpus now. No
further action needed on this item; not refiling.
