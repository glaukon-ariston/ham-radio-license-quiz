# Emit work packets for the 720 book questions

prio:       P2
cluster:    book-notes-prep
files:      quiz/build/make_packets.py
blocked-by:

**Why.** `make_packets.py` reads `Q["questions"]` only, so the 720 `questions_extra` have no
packets. Without one, every P3 notes item has to open the whole 3.5 MB `questions.json` to
reach its 30 questions — tens of thousands of tokens spent before any work starts, on every
one of the 24 items. This blocks the entire P3 band.

**Done when.** `make_packets.py` writes `work/packet_book_s<N>_<section>[_a|_b].json` for all
18 skupina×section groups (tehnički split in half), each carrying the same per-question
fields the HRS packets do, and the counts sum to 720.

**Avoid.** Do not change the existing HRS packet output — the P3 items and the `done`-marker
convention (`links` present means expanded) both depend on its current shape. Book questions
have `subsection: None` today, so do not key anything off subsection until 0002 lands.
