# Classify the 720 book questions into topic subsections

prio:       P2
cluster:    book-notes-prep
files:      quiz/build/parse_book2.py, quiz/build/rebuild.py, quiz/build/make_packets.py
blocked-by:

**Why.** `questions_extra` carries `subsection: None`. The only grouping is *skupina*, and a
skupina is a whole mock exam — 60 technical questions spanning theory, components, circuits
and antennas at once. Every P3 notes item therefore has to load reference material for all
topics. Giving book questions the same subsections the 456 HRS questions already use lets
the grind be re-cut by topic, which is a large one-time saving across 24 items.

**Done when.** Every `questions_extra` entry has a non-null `subsection` drawn from the
existing HRS vocabulary; `make_packets.py` can cut book questions by topic; `rebuild.py`
still reports 1176 questions with no integrity failures.

**Avoid.** Do not guess a topic from the answer. Classify from the question stem against the
priručnik's own chapter structure, and leave genuinely ambiguous ones unset rather than
wrong — a wrong subsection silently misfiles a question forever.
