# Teaching notes: skupina I — pravila i postupci

prio:       P3
cluster:    book-notes-s1-pravila
files:      quiz/build/work/packet_book_s1_pravila.json, quiz/build/notes_book_s1_pravila.json
blocked-by: 0005

**Why.** 40 of the 720 book questions from SKUPINA I. They are answerable and cited
to the priručnik's own key table, but carry no teaching note — the last large body of work
on the corpus.

**Done when.** All 40 have a note in `notes_book_s1_pravila.json`, every citation
verified against the printed page with `booktool.py`, every external link fetched and
confirmed not to be a disambiguation page, and `rebuild.py` still reports 1176 questions.

**Avoid.** These come from one mock exam paper, so the 40 span every topic at once —
landing 0002 first re-cuts this by subject and makes it markedly cheaper. Never restate an
answer as its own explanation, and cite nothing rather than a plausible page.

---

**Recovering the blocked attempt (filed 11 Aug 2026).** A previous attempt wrote all 40
notes and was blocked for one citation defect only; its work is in the stash
`queue P3-0008: fail` (`git stash list`). Recover that stash rather than rewriting from
scratch — the checker verified the other 39 notes.

The defect: `bk-pra-1-27` cites `NN150/22, čl. 2. st. 1. t. 1.` to support "radiopostaja …
jedan ili više odašiljača i prijamnika zajedno s pomoćnom opremom". That article only says
"amaterska radijska postaja: radijska postaja koja radi u radiofrekvencijskom pojasu
namijenjenom amaterskoj službi i amaterskoj satelitskoj službi" — it defines the station by
frequency band, not by equipment. The equipment-based definition exists only in RK's own
exam text, which the note already cites alongside.

**Done when (in addition to the original).** `bk-pra-1-27` either cites a source whose text
actually contains the equipment-based definition, or cites only the RK text and drops the
NN150/22 pointer — per the brief's Avoid clause, cite nothing rather than a plausible
article. Every other citation in the recovered file is re-confirmed word-for-word on its
cited page before you declare done.
