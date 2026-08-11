# Teaching notes: skupina V — tehnički (druga polovica)

prio:       P3
cluster:    book-notes-s5-tehnicki
files:      quiz/build/work/packet_book_s5_tehnicki_b.json, quiz/build/notes_book_s5_tehnicki_b.json
blocked-by: 0005

**Why.** 30 of the 720 book questions from SKUPINA V. They are answerable and cited
to the priručnik's own key table, but carry no teaching note — the last large body of work
on the corpus.

**Done when.** All 30 have a note in `notes_book_s5_tehnicki_b.json`, every citation
verified against the printed page with `booktool.py`, every external link fetched and
confirmed not to be a disambiguation page, and `rebuild.py` still reports 1176 questions.

**Avoid.** These come from one mock exam paper, so the 30 span every topic at once —
landing 0002 first re-cuts this by subject and makes it markedly cheaper. Never restate an
answer as its own explanation, and cite nothing rather than a plausible page.

---

**Recovering the blocked attempt (filed 11 Aug 2026).** A previous attempt wrote all 30
notes and was blocked for one wrong page/section pointer; the checker verified the other
citations clean and independently confirmed the attempt's own findings (6 `has_figure`
mislabels, the `bk-teh-5-32` option truncation). Its work is in the stash
`queue P3-0023: fail` (`git stash list`). Recover that stash rather than rewriting from
scratch.

The defect: `bk-teh-5-54`'s second citation reads "3.4.6. Harmonici… tiskana str. 121", but
the examples it quotes ("Drugi harmonik je f2=2×3530 kHz=7060 kHz"; "Peti harmonik…
f5=720 MHz") are printed on str. 120 under section 3.4.5. Str. 121 carries only the 3.4.6
heading, not those examples — topically adjacent, but the quoted text is not on the cited
page.

**Done when (in addition to the original).** `bk-teh-5-54`'s second citation names the page
and section the quoted examples actually appear on, and every other citation in the
recovered file is re-confirmed by checking that its quoted text is literally present on the
page cited — not merely nearby.
