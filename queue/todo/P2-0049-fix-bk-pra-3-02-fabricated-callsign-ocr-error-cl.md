# Fix bk-pra-3-02 fabricated callsign OCR-error claim, land skupina III pravila notes

prio:       P2
cluster:    book-notes-s3-pravila
files:      quiz/build/work/packet_book_s3_pravila.json, quiz/build/notes_book_s3_pravila.json

**Why.** P3-0016 (skupina III pravila, 40 notes) has been blocked four times. The originally
-named HRD page defect and thirteen more found across two repair rounds are all fixed and
confirmed — see `queue/blocked/P3-0016.why` for the full history. It is blocked a fourth time
on one remaining defect in `bk-pra-3-02`: the note quotes option b) as
`"F5SBDW ? PSE UR CALL AGN de 9A$SJA + PSEK"` and attributes the garbling to "OCR knjige
[koja] unosi grafičke greške u pozivne oznake" (the book's own OCR introducing errors). This
is false — rendered directly, str. 388 question 2 option b) prints
`"F5BDW ? PSE UR CALL AGN de 9A5JA + PSE K,"` cleanly, no garbling. The extraction that
produced the quoted string is the note-writer's own OCR pass, not the book. This is the third
confirmed instance of this exact bug in this one file. Confirmed independently by both the
round-3 checker and Glaukon. See the new rule 7 / trap in `queue/BRIEF.md` — this defect (and
its sibling in P2-0048) is the reason it exists.

**Done when.** Recover stash `queue P3-0016: fail (repair attempt 3)` (`git stash list`;
`git stash show -u <ref> --stat` to confirm it's the right one before applying). In
`bk-pra-3-02`'s note, replace the garbled quoted callsign string and the "OCR knjige" framing
with the actual printed text (`F5BDW ? PSE UR CALL AGN de 9A5JA + PSE K`) confirmed by
rendering str. 388 yourself — do not reuse the old quote as a starting point. The rest of the
note's reasoning (decoding PSE/UR/CALL/AGN, why the answer is b) can stay if it still holds
against the corrected text. `rebuild.py` reports 1176 questions, `explained` includes all 40
of this packet's ids with no "unknown ids" warning for `bk-pra-3-*`, `strict.py` does not
regress below 96.3%.

**Avoid.** Don't re-open any of the other 39 notes — verified clean across three rounds. Given
this file has now shown the same OCR-as-book-error bug three separate times, don't just fix
the one named id: skim the file's other notes for any other quoted call-sign-like or
abbreviation-like string and confirm each against a render, not against memory of what you
already checked in an earlier round.
