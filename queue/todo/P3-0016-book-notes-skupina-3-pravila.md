# Teaching notes: skupina III — pravila i postupci

prio:       P3
cluster:    book-notes-s3-pravila
files:      quiz/build/work/packet_book_s3_pravila.json, quiz/build/notes_book_s3_pravila.json
blocked-by: 0005

**Why.** 40 of the 720 book questions from SKUPINA III. They are answerable and cited
to the priručnik's own key table, but carry no teaching note — the last large body of work
on the corpus.

**Done when.** All 40 have a note in `notes_book_s3_pravila.json`, every citation
verified against the printed page with `booktool.py`, every external link fetched and
confirmed not to be a disambiguation page, and `rebuild.py` still reports 1176 questions.

**Avoid.** These come from one mock exam paper, so the 40 span every topic at once —
landing 0002 first re-cuts this by subject and makes it markedly cheaper. Never restate an
answer as its own explanation, and cite nothing rather than a plausible page.

---

**Recovering the blocked attempt (filed 11 Aug 2026).** A previous attempt wrote all 40
notes and was blocked for a single wrong page pointer inside one compound citation; the
checker verified 30+ other citations clean, including the packet's `hrs_source` off-by-one
correction (SKUPINA III starts str. 388, not 387). Its work is in the stash
`queue P3-0016: fail` (`git stash list`). Recover that stash rather than rewriting from
scratch — this is a one-character fix plus a re-verification pass.

The defect: `bk-pra-3-05`'s compound citation reads "3. Operativne kratice, tiskana str. 253
(HR, FER, FM); **str. 254 (HRD)**; str. 254-255 (SIGS, VY)…". HRD ("čuo, čujem") is defined
on str. 253, directly below the HR row — not on str. 254, whose abbreviation list starts at
LTR and contains no HRD entry. The semantic content is right; only that one sub-page pointer
is wrong.

**Done when (in addition to the original).** `bk-pra-3-05`'s citation points HRD at the page
it is actually printed on, and every other individual page pointer inside every compound
citation in the recovered file is checked separately — a compound citation is only correct
when each of its page numbers is correct.

---

**Round 2 (filed 11 Aug 2026).** Repair attempt 1 fixed the named HRD defect plus twelve
more the checker had missed, six of them false negatives traced to a real root cause:
PyMuPDF's extraction silently drops a label column on RK str. 253 (32 labels extracted for
~45 printed definitions), so any note claiming an absence checked only against extracted
text can come out backwards. It was blocked again on a new defect the repair itself
introduced. Recover the stash `queue P3-0016: fail (repair attempt 2)` — it is 13 fixes
ahead of the original stash named above. Do not recover the original.

The new defect: `bk-pra-3-34`'s cite places „DN - dolje, na nižu frekvenciju" on tiskana
str. 253; DN is printed on str. 252 (253 begins at DX). One character in one `loc` string.

**Done when (round 2).** `bk-pra-3-34`'s page pointer is corrected (253 → 252). Because two
consecutive repair passes on this file have each introduced a fresh wrong page number while
fixing others, after you finish editing, re-check every page number you personally touch —
and separately, every individual page number inside every compound/multi-page citation in
the whole file — against the actual printed page, not against your memory of having gotten
it right. For every absence/negative claim in the file (of the pattern "X is not in the
list", "no source says X"), render the page as an image and read it visually; the PyMuPDF
extraction gap is confirmed real on at least str. 253 and may recur elsewhere in this book.
