# Addendum for the regulatory batches (propisi, pravila)

Read this **after** BRIEF.md. Everything in BRIEF.md still applies; this adds what is specific
to the legal half of the exam, where the danger is not a wrong formula but a note that states
current law as if it were the exam answer, or the reverse.

## The one thing to get right

The HRS answer key is authoritative for **what the examiner marks**. The exam material is older
than the Pravilnik in force and lags it in places. So a good note here does two jobs at once:

1. explains why the marked answer is the marked answer, so Glaukon can score the point; and
2. where the current Pravilnik says something different, says so plainly, so he is not taught
   something false about the law he will operate under.

Never resolve that tension by changing the answer. Never resolve it by hiding the divergence.

## The audit you are inheriting

All 174 regulatory questions were audited article by article on 9 August 2026: 80 confirmed
against the text, 28 marked `check` (amber), 4 marked `conflict` (red). Your packet carries
each question's `flag` and its `current_explanation`, and the audited notes carry a paragraph
beginning **⚖ Provjera propisa:** with the specific article that was checked. That paragraph is
the evidence. Keep its substance in your rewrite — expand it into proper prose, but do not drop
the article reference and do not soften the finding.

> The audit's separate evidence file, `quiz/build/currency_findings.json`, is **gone** — it is
> referenced by the old handoff but no longer exists on disk. `notes_zz_currency.json` and the
> `current_explanation` in your packet are now the surviving record. That is another reason not
> to lose the ⚖ content: there is no longer a backup of it.

### Red — the law contradicts the marked answer (4)

- `pro-047` — 135,7–137,8 kHz is marked "A i P razreda"; Dodatak 1 lists it **A-only**. The
  2005 priručnik independently keys *"samo A razreda"*, so two sources make HRS the outlier.
- `prv-035` — the 10 m band is marked 29000–29700 kHz; the Pravilnik says **28000**–29700 kHz.
- `pro-079`, `pro-080` — both say "prije 01.01.**2013**". The real cut-off is **1 January
  2003**; the string `2013` does not occur anywhere in NN 150/22. Before 1.1.2003 → the dB/mW
  table (čl. 22. st. 4.); after → `43 + 10 log(PEP)` (st. 5.).

### The big amber cluster — inspection powers are not in this Pravilnik at all

`pro-069` and `pro-087`–`pro-092` cited čl. 24., which only covers the licensee's duty to stop
causing interference. In the whole document `inspek` appears once, `kazn` and `zabran` not at
all. Those powers live in the **Zakon o elektroničkim komunikacijama, NN 76/22** — the law this
Pravilnik was issued under and names in its own preamble (čl. 16. st. 1. t. 1. and čl. 69.
st. 22.). Cite `ZEK`, not `NN150/22`, whenever a question is about inspection, penalties,
prohibition or supervision.

Same shape for the logbook questions `pro-072`–`pro-075`: čl. 20. st. 2. expressly permits an
electronic log, so an answer implying a paper-only requirement is out of date.

Also `prv-025`: the answer is right, but for the reason of the **200 Hz bandwidth** limit, not
"samo A1A i F1B" — that is Napomena 3, and it belongs to the 10 100 kHz row, not to 2200 m.

## Verifying an article before you cite it

Do not trust an inherited `čl.` number. Check it:

```
cd quiz/build
python booktool.py find NN150/22 "dnevnik"      # every page mentioning a term
python booktool.py page NN150/22 5
```

Or search the text directly with PyMuPDF. The Narodne novine HTML is also authoritative and
linkable — see LINKS.md. When you cite, give the article **and** the paragraph
(`čl. 20. st. 2.`), because a bare article number is not checkable in a document this long.
If you cannot confirm a number, say so in the note and cite nothing (rule 5).

## What a good regulatory note looks like

Not "the answer is c) because the Pravilnik says so". Say what the rule *is*, why it exists
(interference, international coordination, traceability, safety), what it means in practice at
the operating desk, and where the boundary is that the exam likes to probe — class A versus P,
which bands and which powers, who may set up which kind of station, what must be logged, what
must be reported. Where a number appears (a power limit, a band edge, a bandwidth, a retention
period), put it in a `formula` block as a small table; those are exactly what gets forgotten.

For `pravila` (operating procedures) the same applies to phonetics, Q-codes, callsign
structure, prefixes, band plans, emergency traffic and contest practice: explain the *purpose*
of the convention, because Glaukon will remember a reason far longer than a list.
