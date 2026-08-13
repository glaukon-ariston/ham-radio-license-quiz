# Teaching notes: skupina II — pravila i postupci

prio:       P3
cluster:    book-notes-s2-pravila
files:      quiz/build/work/packet_book_s2_pravila.json, quiz/build/notes_book_s2_pravila.json
blocked-by: 0005

**Why.** 40 of the 720 book questions from SKUPINA II. They are answerable and cited
to the priručnik's own key table, but carry no teaching note — the last large body of work
on the corpus.

**Done when.** All 40 have a note in `notes_book_s2_pravila.json`, every citation
verified against the printed page with `booktool.py`, every external link fetched and
confirmed not to be a disambiguation page, and `rebuild.py` still reports 1176 questions.

**Avoid.** These come from one mock exam paper, so the 40 span every topic at once —
landing 0002 first re-cuts this by subject and makes it markedly cheaper. Never restate an
answer as its own explanation, and cite nothing rather than a plausible page.

---

**Recovering the blocked attempt (filed 11 Aug 2026).** A previous attempt wrote all 40
notes and was blocked for three citation defects; its work is in the stash
`queue P3-0012: fail` (`git stash list`). Recover that stash rather than rewriting from
scratch.

The three defects:
1. `bk-pra-2-12` lists "76-81 GHz, **122-136 GHz**, 241 GHz" as all "nije preporučljivo s
   obzirom na sekundarnu dodjelu". RK str. 279 shows 134,001–136,000 GHz as *sve vrste
   emisija | preporučuje se s obzirom na primarnu dodjelu* — primary and recommended, the
   opposite of the claim. The real "not recommended / secondary" segment is 136,000–141,000
   GHz, and 122,250–123,000 GHz carries no such note at all.
2. `bk-pra-2-18` prose asserts "Plan pojaseva za LARU Regiju 1', str. 271", but that phrase
   is on RK str. 267 — which the note's own `cite` field already gets right. The prose
   contradicts its own citation.
3. `bk-pra-2-29` claims the segment "do 7 045 kHz" is "rezerviran isključivo za
   telegrafiju/digitalne načine rada", but RK str. 264 (the page it cites) lists 7040–7045
   kHz as *digitalna (osim paketne), SSTV, FAX, telegrafija, telefonija* — telefonija is
   already permitted, so "isključivo" is wrong.

**Done when (in addition to the original).** All three are corrected against the real page
text, any inline page number in note prose matches that note's own `cite` field, and every
other citation in the recovered file is re-confirmed word-for-word before you declare done.

---

**Round 2 (filed 11 Aug 2026).** Repair attempt 1 fixed all three defects above and nine
more the checker had missed — 12 fixes total, all independently confirmed. It was blocked
again on a thirteenth. Recover the stash `queue P3-0012: fail (repair attempt 2)` — it is 12
fixes ahead of the original stash named above. Do not recover the original.

The new defect: `bk-pra-2-28` asserts of option a) (TX/RX 145,750/145,150) that "Opcija a)
navodi brojke koje ne pripadaju nijednom retku tablice". RK str. 280 — the note's own cited
page — lists `RV60  145,150  145,750  R6`, exactly that pair. The claim is contradicted by
its own citation.

Also cosmetic: the file's `_note` field says "još šest" but then lists twelve ids — fix the
count while you're in there.

**Done when (round 2).** `bk-pra-2-28`'s claim about option a) is corrected or removed, the
`_note` count is fixed, and — because this file's repair passes have now twice introduced
new errors while fixing old ones — every one of the 40 notes is read once more as a
standalone claim (not diffed against the round-1 fix list) and checked against actual page
text, including every negative/absence assertion, which must be checked against a rendered
page image, not extracted text alone.

---

**Closed out, superseded (12 Aug 2026).** notes_book_s2_pravila.json landed via P2-0051
(round 9), which recovered this item's own stash lineage and fixed every remaining defect.
The checker for that round rendered all 26 cited pages and verified every quoted string
character-by-character across all 40 notes — the file is in the committed corpus now. No
further action needed on this item; not refiling.
