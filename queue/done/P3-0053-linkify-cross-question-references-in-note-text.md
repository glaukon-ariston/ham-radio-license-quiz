# Linkify cross-question references in note text

prio:       P3
cluster:    note-crosslinks
files:      quiz/quiz.html, quiz/build/rebuild.py
blocked-by:

**Why.** About 230-260 of the 1176 notes (`q.e`) mention another question by id in prose —
e.g. `teh-141`: "Ne brkati s osjetljivošću (**teh-142**)"; `pro-091`: "Usporedi s **pro-090**";
`bk-teh-5-26`: "vidi pitanje 24". The quiz already has a working per-question permalink
(`#q=<id>`, built by `qidFromUrl`/`setUrlQ` in quiz.html around lines 788-821, and rendered
as the tag's own `href` at quiz.html:500) but note text is inserted as plain `textContent`
(quiz.html ~541-550, with a comment explaining why: it may contain stray `<`/`&` from quoted
regulation text). So these references read as dead text — a user has to close the note,
search the id manually, and reopen. Making them clickable costs nothing once the id is
already in the string.

**Done when.** Notes whose text contains a token matching an existing question id (pattern
like `teh-\d{2,3}`, `pro-\d{2,3}`, `prv-\d{2,3}`, `pra-\d{2,3}`, `bk-\w+-\d-\d+`) render that
token as `<a href="#q=<id>">` inside the note body, using the existing deep-link mechanism —
clicking it jumps to that question exactly like the permalink tag does. Every linkified id
must be checked against the actual set of ids in the built `quiz/questions.json`; a token
that doesn't resolve to a real id is left as plain text, not linked to a dead anchor.
`python quiz/build/rebuild.py` and `python quiz/build/strict.py` still pass at the same
1176/95.4%-or-better baseline. Report roughly how many notes ended up with at least one
working cross-link.

**Avoid.** Do not attempt to resolve the bare-number book references ("vidi pitanje 24" with
no id, mostly in `notes_book_s*_tehnicki_*.json`) — mapping a plain number to the right
`bk-*` id needs the book's own subsection numbering and is a separate, riskier problem; leave
those as plain text and name them in the report instead of guessing. Keep the note body a mix
of text nodes and `<a>` elements built via DOM calls (`document.createElement`), not a switch
to `innerHTML` on the whole string — the existing comment at quiz.html:541-542 explains why
raw HTML injection into note text is unsafe (it can carry unescaped `<`/`&` from quoted
regulation prose). Don't touch the external-link rendering path (`q.lk`) or `link_check.py`,
which is unrelated.
