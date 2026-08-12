# Fix bk-pra-2-05 and bk-pra-2-31's fabricated line-split claims, land skupina II pravila notes

prio:       P2
cluster:    book-notes-s2-pravila
files:      quiz/build/notes_book_s2_pravila.json
blocked-by:

**Why.** P2-0048 blocked a fourth time on two notes that each claim the printed book splits a
short quoted line across two printed lines, and that `packet_book_s2_pravila.json`'s own
`question`/`answer_text` field is truncated as a result. Glaukon rendered both pages directly
(RK, `booktool.py`'s printed-page map, 3x zoom) and confirmed both claims are false — see
`queue/blocked/P2-0048.why` for the finding and `git show dda8b42:queue/reports/P2-0048.md`
for the full prior history.

- `bk-pra-2-05` (SKUPINA II, pitanje 5, tiskana str. 383): the note says "Tiskano pitanje
  ispisuje kraticama dva retka: '= UFB DR OM' i '= PSE UR QSL VIA BUREAU' (paket u ovoj bazi
  prikazuje samo prvi redak teksta pitanja...)". Rendered str. 383 prints this as **one
  unbroken line**: "= UFB DR OM = PSE UR QSL VIA BUREAU". The packet's own `question` field
  ends at "= UFB DR OM" — that truncation is a defect in whatever built
  `packet_book_s2_pravila.json`, not a line break in the book.
- `bk-pra-2-31` (SKUPINA II, pitanje 31, option c, tiskana str. 386): the note says
  "...(opcija c; tiskana stranica taj odgovor ispisuje u dva retka, pa ga baza prikazuje
  skraćeno)". Rendered str. 386 prints option c) as **one unbroken line**: "hvala za lijepu
  vezu i odličan raport – nadam se ponovnom susretu i mnogo pozdrava". The packet's own
  `answer_text` field ends at "...odličan raport" — same failure mode, not a book line break.

This is the same class of bug as `bk-pra-2-18`/`bk-pra-3-02` (BRIEF.md rule 7): an extraction
artifact mistaken for a property of the book itself. It has cost this one file four blocked
rounds; this item names the fix precisely so a fifth round isn't needed.

**Done when.** Recover the stash `queue P2-0048: fail` (`git stash list`; if it has been
dropped, the same content is at commit `dda8b42` —
`git show dda8b42:quiz/build/notes_book_s2_pravila.json`). In both notes, remove the sentence
claiming the book prints the quoted text across two lines, and state instead (in your own
words, keeping the rest of each note intact) that the book prints it as one line and the
packet's own field is the one that is truncated. The abbreviation-by-abbreviation
translations in both notes are already correct and verified — do not rewrite them, only the
sentence that misattributes the truncation. `git add` the file (it has never been committed —
this is a first-time landing, not a diff). `python quiz/build/rebuild.py` reports 1176
questions with all 40 `bk-pra-2-*` ids in `explained` and no unknown-id warning.
`python quiz/build/strict.py` does not regress below 96.3%.

**Avoid.** Do not re-open or re-verify the other 38 notes in this file. Three prior rounds
(P3-0012 twice, P2-0048 once) already found and fixed 15 distinct citation defects across
them, and the last pass sampled 17 further citations clean — re-litigating them risks
introducing a fifth defect, which is exactly what happened on both of this file's last two
repair attempts. Do not re-derive the two page renders from scratch to "double check" the
finding above — it is already confirmed by direct human inspection of the rendered pages, not
by `booktool.py`'s extracted text, which is the thing that was wrong in the first place.
