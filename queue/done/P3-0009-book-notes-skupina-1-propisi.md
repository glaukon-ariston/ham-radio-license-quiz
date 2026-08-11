# Teaching notes: skupina I — propisi

prio:       P3
cluster:    book-notes-s1-propisi
files:      quiz/build/work/packet_book_s1_propisi.json, quiz/build/notes_book_s1_propisi.json
blocked-by: 0005

**Why.** 20 of the 720 book questions from SKUPINA I. They are answerable and cited
to the priručnik's own key table, but carry no teaching note — the last large body of work
on the corpus.

**Done when.** All 20 have a note in `notes_book_s1_propisi.json`, every citation
verified against the printed page with `booktool.py`, every external link fetched and
confirmed not to be a disambiguation page, and `rebuild.py` still reports 1176 questions.

**Avoid.** These come from one mock exam paper, so the 20 span every topic at once —
landing 0002 first re-cuts this by subject and makes it markedly cheaper. Never restate an
answer as its own explanation, and cite nothing rather than a plausible page.

---

**Recovering the blocked attempt (filed 11 Aug 2026).** A previous attempt wrote all 20
notes and was blocked for one citation defect only; its work is in the stash
`queue P3-0009: fail` (`git stash list`). Recover that stash rather than rewriting from
scratch.

The defect: `bk-pro-1-16` claims "Dodatak 1., t. 2.4.3. dopušta relejne postaje upravo na
144-146 MHz, 430-440 MHz i 1240-1300 MHz". NN150/22 Dodatak 1 §2.4.3 is titled "Amaterski
radiofar" and only sets beacon ERP limits (50/10/1 W) — it says nothing about repeater
bands. The real source for that band list is RK printed str. 245 ("Amaterska relejna postaja
može raditi u frekvencijskim pojasima 144…146 MHz, 430…440 MHz i 1 240…1 300 MHz"), which
the note does not cite for this claim.

**Done when (in addition to the original).** `bk-pro-1-16` cites the source that actually
carries the band list, and every other citation in the recovered file is re-confirmed
word-for-word on its cited page before you declare done.
