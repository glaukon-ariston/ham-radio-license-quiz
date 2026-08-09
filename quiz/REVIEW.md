# Review notes — things a human should decide

Companion to `../QUIZ_PLAN.md`. Written 8 August 2026.

---

## 1. The book import — QUARANTINE LIFTED (corrected 8 Aug 2026)

**Earlier conclusion was wrong and has been reversed.** An earlier version of this document
said the book's answer key could not be trusted, on the basis of 46 % agreement with the HRS
red key. That number was produced by a bug in *my* parser, not by any fault in the book.

Glaukon spotted it: the MUF question I cited as "Skupina II, pitanje 18, str. 303" is in fact
**pitanje 22 on printed page 302**. Key table row 22, column Skupina II reads **D** =
*"Jednaka MUF-u"* — which is both the physically correct answer and exactly what the HRS red
key marks. The book was right all along; my parser had mis-numbered the question and therefore
read the wrong row of the key table.

### Root cause

The first parser associated question numbers by OCR reading order. The OCR emits the number
column separately from the text column, drops many numbers entirely, and mangles others
(`u.` for `11.`). Result: 39 colliding IDs and 148 questions with no number at all.

The rebuilt parser (`build/parse_book2.py`) instead uses **coordinates**: the number column
sits at x < 80, the stem and left option column at x ≈ 90, the right option column at x ≈ 307,
and these margins alternate between recto and verso, so columns are detected per page.
Option letters OCR badly (`(€)` for `(c)`), so options are taken **by position**.

### The rule that matters

Inferring a question's number from its sequential position was tried and **deliberately
dropped**: it raised coverage to 557 questions but pushed agreement down to 62 %, because any
split or merged block silently shifts every question after it onto the wrong key row.

**A number is taken only from an OCR'd anchor on the question's own baseline.** Questions whose
number the OCR lost are discarded rather than guessed. Fewer questions, all verifiable.

### Recovering the questions whose number the OCR lost

**The book import is now COMPLETE: all 720 questions, every one of the 18 skupine full.**

Block detection was fixed first: a new question is recognised when the CURRENT one already has
four options, instead of when the stem exceeds 20 characters. The old rule silently dropped
short stems such as *"Radioamater je::"* (16 chars).

Then the anchors-only rule was relaxed — but only into gaps where the number is **arithmetically
forced**, never by global position. The reasoning rests on an observation that is itself
checkable: across every skupina the offset between a question's OCR'd number and its position in
the block sequence is **monotonically non-decreasing**. That is the signature of *dropped*
blocks only — a split or merged block would push the offset backwards. So:

1. Anchors are filtered to the longest run with non-decreasing offset, which discards OCR
   misreads (a stray `1.` read at position 11 in propisi I, for example).
2. Between two surviving anchors, the count of unnumbered blocks is compared with the count of
   missing numbers. **When the two are equal, exactly one assignment is possible** and it is
   applied; when they differ, a block was dropped inside that gap and it is left alone.
3. A skupina holding more blocks than expected is refused outright — surplus blocks are the tell
   that the monotonicity argument does not hold there.

This replaced an earlier all-or-nothing "sequence verified intact" test, which could only rescue
a skupina where *nothing* had gone wrong anywhere (4 of 18 qualified). Gap interpolation reasons
interval by interval, so a single bad patch no longer forfeits the whole skupina.

**Independent corroboration.** The OCR misreads some numbers as letters (`52.`→`s2.`,
`11.`→`u.`). Glyph repair recovers these, and they are deliberately **not** used for numbering —
only to check it. Where a repaired glyph and gap arithmetic both speak, they rest on unrelated
evidence (letterform vs. block counting), and they agree **19 / 19**.

**Eye verification.** 13 interpolated questions, sampled one per skupina, were checked against
the rendered page: all 13 printed numbers match the inferred number, none contradicted. The
method is a `pymupdf` clip at the block's baseline.

### Recovering the blocks the parser never built

Interpolation can only number blocks that exist. Six further defects were each traced to a page
and fixed at the cause rather than patched per question:

| Defect | What the OCR did | Fix |
|---|---|---|
| **Merged number + stem** | `3. — Amplituda nemoduliranog vala...` as ONE line in the number column — matching neither the number pattern nor the stem-x test, so the whole question was discarded | parse that line for both an anchor and a stem (**55 questions**) |
| **Misread merged number** | `I. Rad amaterske postaje...` for `1.` | same, but the number goes to the corroboration tier since it is only as good as the glyph |
| **Shifting option columns** | a figure beside the options moves the right-hand column, and by a different amount per question | cluster the option x-positions per page and accept any column the page actually uses |
| **Unused boundary evidence** | a number was recorded as an anchor but never used to split blocks, so a question whose predecessor was still short of four options was swallowed whole | a number on a line forces a block boundary — but only once options have started, since a number's baseline often falls *between* the two lines of its own wrapped stem |
| **Page footers as question numbers** | `288`, `364` sit in the number column and were attached to whatever question began near them | accept a number only if it is within the skupina's range |
| **`u.` suppressed itself** | `u.` (the OCR's `11.`) also matches the *option-label* pattern, so it was counted as an option column, which then made the guard reject its own repair | only options carrying TEXT may define a column |

That last one was the most costly: it silently deleted **every question 11 in the book**.

### The last 31: read by eye

Thirty-one questions remained unreachable by any parser, for reasons that are properties of the
source rather than bugs: two questions run together with no number between them; all four options
set in one full-width column instead of two; and options that **are** diagrams, with no option
text in the book at all. These were transcribed from the rendered pages and recorded in
`build/book_overrides.json`, each with its page and the reason it needed a human.

Crucially, only the **wording and the option order** come from the transcription. The **answer**
still comes from the book's own key table, so a transcription slip cannot invent an answer — at
worst it mis-orders options, which the strict cross-check would catch.

Six of them answer with a picture (filter responses, oscillograms, C-class diagrams). Those are
cropped by `build/book_figures.py`, which imports `figures2.postprocess` rather than copying it,
so the red-neutralisation rule cannot drift apart between the two figure paths.

### Result

| Measure | Value |
|---|---|
| **Book questions** | **720 / 720 — all 18 skupine complete** |
| — numbered from an OCR anchor | 518 |
| — numbered by forced gap interpolation | 171 |
| — read by eye (recorded in `book_overrides.json`) | 31 |
| Colliding IDs | 0 |
| Comparable against the HRS red key (strict) | 107 |
| **Agreement** | **102 / 107 = 95.3 %** |
| — of those numbered from an OCR anchor | **79 / 79 = 100 %** |
| — of those numbered by interpolation | 23 / 28 |

Validation is **strict**: a pair counts only when the stems match *and* the four options match as
a set. Two separate artefacts had to be removed before the number meant anything:

1. the loose text-similarity matcher pairs generic stems (*"Filtar na slici je:"*, *"Sklop na
   slici je:"*) with the wrong HRS question, so the option sets must coincide as well; and
2. `"10 W"` and `"100 W"` score 0.857 on plain similarity, which paired a 2005 question with its
   modern replacement and reported it as a key disagreement — numeric options must now have
   identical digits.

All five surviving disagreements were checked by hand and **none is a numbering error**. Three
had their printed number confirmed on the page image (12, 52, 11):

- **`bk-pro-4-06` vs `pro-047`** — the book marks *"samo A razreda"* for 135,7 kHz, which is what
  Dodatak 1 says. This **independently corroborates the `pro-047` conflict below**: the HRS red
  key is the outlier, not the book.
- **`bk-pra-5-05`** asks about **USB** where HRS asks about **LSB** — different questions the
  matcher paired on a one-letter stem difference. Both keys correct.
- **`bk-teh-3-12`** (number 12 confirmed on str. 306) — *omjer transformacije* for 75 Ω → 300 Ω:
  the book marks 1:2 (turns ratio), HRS marks 1:4 (impedance ratio). A terminology difference,
  and both are defensible; z-ratio 4 ⇒ n-ratio 2.
- **`bk-teh-4-52`** (number 52 confirmed) — suppressing *sub*harmonics **and** harmonics: the book
  marks band-pass, HRS marks low-pass. The book has the better physics here, since a low-pass
  filter cannot suppress a subharmonic. Answer HRS in the exam.
- **`bk-pro-2-11`** (number 11 confirmed) — inspection powers; an edition difference in the law.

Two further edition differences surfaced once the missing questions were recovered, and are worth
knowing because the 2005 book is simply out of date on both:

- **`bk-pro-3-02`** — P-razred PEP: the book offers 150 / 25 / 10 / 75 W and keys **75 W**. The
  current question uses **100 W**, which is not even among the book's options.
- **`bk-pro-1-12`** — the 12-year age limit, removed by NN 150/22 (čl. 9. sets no minimum).

These 720 are served in the quiz as **extra practice, tagged "priručnik"**. They are excluded
from exam simulation, which draws only from the official HRS lists, since those are what clubs
actually use (Odluka t. 12). Each carries its `num_source`, and questions whose number was
reconstructed rather than read say so in their citation.

### Two further text fixes

Eleven stems began with a lowercase fragment — a wrapped option line from the *previous* question
glued onto the next stem (*"neznatno oslabljeni Koje područje ionosfere…"*). A stem always opens
with a capital, so a lowercase line arriving at stem-x after a question has closed is now
appended to that question's last option instead.

The two option columns are also sometimes flattened onto one line with the column gap read as
`=` (*"devijaciju ... nositelja = (d) promjenu ..."*). That is now split — but only when it yields
exactly two substantial halves, because option text legitimately contains parenthesised letters
(*"točka (A)"*, *"Frekvencija (f)"*) and splitting on those destroys real options.

---


## 2. Still outstanding

### Teaching notes — 456 of 456 COMPLETE

Every official question has an explanation with at least one citation (verified
programmatically at build time), shown in the quiz after you answer in practice mode.

| Section | Explained |
|---|---|
| Tehnički | **282 / 282** |
| Propisi | **95 / 95** |
| Pravila i postupci | **79 / 79** |

Citations by source: PZM 283, NN150/22 112, RK 70, TR61-01 6, OBVEZNI 3, TR61-02 2, ERC32 2,
ODLUKA 2, HRS-A 1.

Textbook page anchors used for technical citations (PZM = Pašarić, printed pages), recovered by
extracting chapter 3 headings by font size:

| Topic | str. |
|---|---|
| Tema 1–3, električna teorija | 61–72 |
| 3.2 Komponente / kondenzatori / transformator / diode / tranzistori | 73 / 76 / 83 / 86 / 94 |
| 3.3 Krugovi / rezonancija / oscilatori | 97 / 100 / 103 |
| 4. Prijamnici | 107 |
| 5. Odašiljači (CW 110, AM 111, SSB 112, FM 113) | 110 |
| 6. Antene | 114 |
| 7. Rasprostiranje | 118 |
| 8. Mjerenja | 121 |
| 9. Smetnje / decibel | 125 / 126 |
| 10. Električna sigurnost | 130 |

Citation format: `{src, loc}` where `src` is a key in the `_sources` registry of
`questions.json` (NN150/22, RK, PZM, ODLUKA, OBVEZNI, TR61-01, TR61-02, ERC32, HRS-A).
`RK` locations are **printed** page numbers. Every question also carries `cite_self`
pointing at where it lives in its own source list.

### Currency pass — DONE for the band and power questions

Checked directly against the extracted text of NN 150/22. **The propisi bank is current**, not
stale: it already speaks of *Agencija* (HAKOM), CEPT T/R 61-02, ERC Report 32, samogradnja
certification by HRS, and the 70 MHz band — all NN 150/22-era concepts.

Verified correct against Dodatak 1, Tablica 1: `pro-048` `pro-049` `pro-050` `pro-051`
`pro-052` `pro-053` `pro-055` `pro-056` `pro-058` `pro-059` `pro-071`, and `pro-044`
(*"razmacima od najmanje deset minuta"*).

#### ⚠ One real conflict: `pro-047`

> *Frekvencijski pojas od 135,7 kHz do 137,8 kHz može upotrebljavati radioamater:*
> HRS red key marks **b) A i P razreda**.

In Dodatak 1, Tablica 1 the string `135,7` occurs exactly **twice** in the whole Pravilnik: once
as a row in the **A-razred** table (status S, 1 W EIRP, 200 Hz) and once in Napomena 4. It does
**not** appear in the P-razred table, whose HF allocation is only 3500–3800, 7000–7200,
14040–14150, 14280–14350, 21000–21450 and 28000–29700 kHz.

**Under current law the answer is d) samo A razreda.** The quiz shows a red
"Propis kaže drugačije" panel on this question. Answer HRS's key in the exam; know the law.

Worth raising with the club — it may be a known erratum.

#### ? Minor discrepancy: `pro-034` (rok za prijavu promjene)

HRS marks **"u roku od dva tjedna"** (14 days). Čl. 12. st. 16. says *"bez odgode, a najkasnije
u roku od 15 dana od dana nastanka promjene"*. One day apart — almost certainly loose wording in
the exam list rather than a substantive difference. Flagged amber.

#### ⚠ Second conflict: `prv-035` (10 m band)

> *Koji dio 10-metarskog područja u Republici Hrvatskoj namijenjen radioamaterima?*
> HRS red key marks **b) 29000 – 29700 kHz**.

Dodatak 1, Tablica 1 lists the 10 m band as **28 000 – 29 700 kHz**, for both A and P razred.
Option **c) 28000 – 29700 kHz** is what the Pravilnik says. Flagged red in the quiz.

#### ? Probable error, needs the club: `prv-057` (locator)

> *Što određuju prve znamenke univerzalnog lokatora?*
> HRS marks **c) 10° dužine i 20° širine**.

Under the Maidenhead standard the first field spans **20° of longitude and 10° of latitude** —
the reverse — which is offered as option b). Arithmetic check: 18 fields x 20 deg = 360 deg of
longitude, 18 x 10 = 180 deg of latitude. The priručnik does not define the locator in its
reference text (only inside exam questions), so unlike `pro-047` and `prv-035` there is no
Croatian document to cite against. Flagged amber "Provjeriti s klubom" rather than red.

#### Imprecise rather than wrong: `pro-057`

Asks the A-class PEP limit "na 50 MHz". The table splits 6 m: 50 000–50 500 kHz = **500 W**,
50 500–51 900 kHz = **100 W**. 500 W is not among the options, so the marked 100 W is the only
defensible choice offered — but the question does not say which half of the band it means.

### Currency audit — DONE, all 174 regulatory questions (9 Aug 2026)

Every `propisi` (95) and `pravila` (79) question was checked article by article against
NN 150/22. Results: **80 confirmed**, **28 flagged amber**, **4 flagged red**. Findings with a
verbatim Croatian quote for each are in `build/currency_findings.json`; the corrections are
applied through `build/notes_zz_currency.json` (named to sort last so its citations win).

**The HRS answer was never changed.** It stays authoritative for what the examiner marks; what
changed is the citation and what the note tells you.

#### Two new red conflicts — a ten-year date error

`pro-079` and `pro-080` both say *"stavljene u uporabu prije 01.01.**2013**."*. The Pravilnik's
cut-off is **1. siječnja 2003.** — the string `2013` does not occur anywhere in NN 150/22.
This matters, not just pedantry: for equipment put into use 2003–2013, which the question's own
wording covers, čl. 22. **st. 5.** applies (`43 + 10 log(PEP)` ili 50 dBc), not the marked
dB/mW table from st. 4. `pro-081` carries the same wrong date but its answer survives it (amber).

Learn the pair: **before 1.1.2003 → the dB/mW table; after → the 43 + 10 log formula.**

#### The largest amber cluster: inspection powers are not in this Pravilnik

`pro-069` and `pro-087`–`pro-092` all cited **čl. 24.**, which is about the licensee's own duty
to stop causing interference — it says nothing about inspection. Across the whole Pravilnik:
`inspek` occurs **once** (čl. 22. st. 7.), `kazn` **zero** times, `zabran` **zero**. The phrase
*"dvadeseterostruka prosječna plaća"* in `pro-087` appears nowhere; it is language from the old
Zakon o telekomunikacijama.

Those powers live in the **Zakon o elektroničkim komunikacijama, NN 76/22** — the law under
which this Pravilnik was issued, named in its own preamble (čl. 16. st. 1. t. 1. i čl. 69. st.
22.). ZEK is now in the `_sources` registry. The answers are probably right; they simply cannot
be verified from the Pravilnik, so they are amber rather than green.

Four logbook questions (`pro-072`–`pro-075`) are the same shape: `olovk`, `prazn` and `uvezan`
all return zero hits, and čl. 20. st. 2. expressly permits an **electronic** log — which sits
awkwardly with answers about pencils and bound books.

#### `prv-025` — right answer, wrong reason (now corrected)

The old note said telephony is barred from 135,7–137,8 kHz because only A1A and F1B are allowed.
That is **Napomena 3, and it belongs to the 10 100 – 10 150 kHz row.** The 2200 m row carries
**Napomena 4** (EIRP max 1 W). What actually excludes telephony is the **200 Hz** maximum
bandwidth in Tablica 1 — a voice signal does not fit. Note rewritten.

#### `pro-057` now flagged

Already described below but never surfaced in the UI. Tablica 1 splits 6 m: 50 000–50 500 kHz =
**500 W**, 50 500–51 900 kHz = 100 W. *"Rad na 50 MHz"* literally falls in the 500 W segment,
which is not among the options. Amber.

#### Also worth knowing

`pro-040`/`pro-041` (CEPT guest callsigns) were citing T/R 61-01 Aneks II; the operative rule is
**čl. 15. st. 2. t. 2.** `prv-026`–`prv-030` describe IARU R1 bandplan edges, which are not
legally binding at all and can drift from the current bandplan. The HRS Odluka behind
`pro-017`/`pro-021` still rests on the repealed NN 45/2012.

### Remaining currency work

The red key is authoritative for **what the examiner marks**, but the HRS exam material may
itself lag current law. These must be checked article by article, and where they disagree
**both** recorded — you want to answer what the examiner expects while knowing the real
legal position.

Highest-risk areas, from `PLAN.md`:

- **Dodatak 1, Tablica 1** — band edges, power limits and P/A class per band
- Any question naming the issuing body (HAKOM vs "Ministarstvo")
- Licence validity periods and callsign format (čl. 15. st. 1.)
- The 10-minute identification interval (čl. 15. st. 3.) — *already confirmed*: `pro-044`
  independently resolves to "10 minuta", matching the current Pravilnik

---

## 3. Judgement calls already made

Recorded in `build/overrides.json` with reasons. Summary:

- **`teh-186b`** — technical question 186 is followed by an **unnumbered question** in the
  source PDF ("Duljina strane quad radijatora i polarizacija su:"). Kept, numbered `186b`.
- **`teh-030`** — the literal string "(f)" inside the answer *Frekvencija (f)* was being read
  as an option label.
- **Four questions whose options are diagrams** (`teh-074`, `075`, `095`, `114`). The red mark
  still identifies the answer; the options are served as a cropped image.
- **27 of 45 figure crops contained red answer marks**, which would have given the answer away
  in the quiz. Red is recoloured to black in every crop. This neutralisation lives inside
  `build/figures2.py` — it was once a separate ad-hoc script, and a later rebuild silently
  restored the red marks. Keep it in the cropping step.
- **`teh-192` citation corrected.** The question asks the minimum distance from the antenna to
  **space where people are** — an EMF-protection limit (5 m), which is NOT in NN 150/22. My
  first note wrongly cited čl. 21 and described it as clearance to telecom lines. Čl. 21 is a
  different rule: **1 m** to public communications installations, which is what `pro-076` asks.
  Both notes now state the distinction explicitly.
- **Three questions whose formulas are images in the source PDF** and therefore vanished or
  came out as control characters. Transcribed by eye from rendered pages and recorded in
  `build/overrides.json`: `teh-017` (question lost "Uef = 100 V"), `teh-020` (Ohm's-law
  equations), `teh-081` (Thomson formula, str. 13).
- **`teh-074` was unanswerable and is fixed.** The four HRS diagram-option questions carried
  only whichever option labels happened to land on a text baseline — `teh-074` offered a) and
  c) alone, while its correct answer is **b)**. All four (`teh-074`, `075`, `095`, `114`) now
  list their labels explicitly in `build/overrides.json`; `teh-114` keeps its real fourth
  option, *"ni jedan od prikazanih"*. A build-time assertion now checks that every question's
  answer is among its options, so this class of defect cannot return silently.
- **31 book questions read by eye**, recorded in `build/book_overrides.json` with page and
  reason. Answers still come from the book's key table, never from the transcription.

---

## 4. Expansion pass, 9 August 2026 — defects found while rewriting the notes

Rewriting all 456 explanations meant re-reading every citation against the page it names.
That turned up a class of defect the earlier passes could not have seen, because the earlier
passes trusted the inherited citations.

### ⚠ Three of the four diagram-answer questions were keyed WRONG

Section 3 above records that the four diagram-option questions had their labels supplied by
hand in `build/overrides.json`. What it did not record is that **the answers typed in beside
those labels were also hand-entered, and three of the four were wrong.** Verified against the
red span in `docs/RA_ispiti_9_A_razred_Tehnicki_dio.pdf`:

| id | was | HRS actually marks | the wrong answer taught |
| --- | --- | --- | --- |
| `teh-075` | `c` | **`d`** | a U-shaped curve instead of the 3 kHz low-pass |
| `teh-095` | `a` | **`b`** | an un-rectified sine as a half-wave rectifier output |
| `teh-114` | `a` | **`c`** | correct modulation shown as overmodulation |
| `teh-074` | `b` | `b` ✓ | — |

`teh-114` is corroborated three ways: the red span, the figure itself, and RK 5.4.10
(tiskana str. 144) — *"Kada imamo 100 posto modulaciju trapez će prijeći u trokut"*, so a
trapezoid cannot be overmodulation. All three are corrected, each with its reason in the file.

**This is not a rule-1 violation.** Rule 1 forbids substituting our judgement for the
examiner's key. Here our *transcription* of the examiner's key was wrong, and the fix restores
it. To re-check all four at once, list the coloured spans falling between a question's stem
and the next question's stem.

### The figure extractor had three separate faults

- **`teh-186` showed the wrong picture entirely** — the quad loop belonging to the unnumbered
  `teh-186b`. An unnumbered question cannot anchor a boundary, so 186's extent ran past its own
  polar plot and its crop landed on 186b's drawing. `figures2.py` now anchors unnumbered
  questions by their stem text. Both questions now get their own figure (46 figures, was 45).
- **`teh-043` was a 181×41 sliver.** A figure's own labels ("25 Ω", "= 5 V") are text cells, so
  "below the last text line" put the crop band underneath the circuit, on blank paper.
- **`teh-074`'s figure sits above its options**, the opposite layout, so any single rule gets
  one of the two wrong. The extractor now renders both candidate bands and keeps the tightest
  one that actually contains ink.

### ~~`teh-024` is unanswerable and it is not our bug~~ — WRONG, see §5

### ⚠ New legal conflict outside the audited 32: `teh-192`

The question teaches that an antenna must be **5 m** from other installations. `čl. 21. st. 1.`
of NN 150/22 prescribes **"najmanje jedan metar"**, and it is a distance to a *public
communications installation*, not to people. The string "5 m" occurs **zero** times in the whole
Pravilnik. Flagged `check`; the exam answer is kept.

**The gap this reveals:** the currency audit covered the 174 `pro-`/`prv-` questions. Technical
questions with legal content were never audited, and `teh-192` is one.

That gap has since been swept: all 282 `teh-` questions were scanned for legal vocabulary
(*pravilnik, zakon, propis, dozvola, razred, dopušteno, nadzor, kazna, zabrana, udaljenost,
ograničenje*). 18 matched, and 16 are false positives — *Ohmov zakon* is a law of physics and
*C razreda* is an amplifier class, not a licence class. Only two carry real regulatory content:
`teh-192` (above) and `teh-281` (RF exposure, `čl. 12. st. 2.`, verified). **Both are handled,
so the technical section holds no further unaudited legal claim.**

### `prv-026` — a ten-kilohertz typo in the exam material

The marked answer gives the 15 m phone segment as starting at **21161 kHz**. RK, tiskana
str. 265, prints `21 151....21450kHz telefonija, telegrafija, SSTV, FAX`, and the current IARU
R1 HF band plan agrees: **21151 kHz**, with 21149–21151 reserved for beacons. Almost certainly
a digit typo. Option (d) is still the only viable answer, so the key stands, but the note tells
the reader to memorise 21151 as the real edge.

(A grep for `21151` finds nothing — the OCR writes it `21 151`, with a space. Search RK for
spaced digit groups, or the number will look absent when it is on the page.)

### One root cause behind the `pravila` flags

`prv-026`, `prv-028` and `prv-030` are all flagged for the same reason, now stated in each
note: **NN 150/22 regulates only band edges and maximum bandwidth** (Dodatak 1., Tablica 1.;
čl. 16. st. 2.) and never mode segmentation — the single exception being Napomena 3
(10 100–10 150 kHz, A1A/F1B only). Everything the exam asks about "where phone starts" is IARU
convention, not Croatian law. Worth keeping in mind before flagging a fourth one.

### Two more HRS-vs-handbook divergences in `9. Smetnje`

RK reprints 13 of the 15 interference questions verbatim in its *Zbirka ispitnih pitanja*, so
its answer table can be compared with the HRS red marking. Two disagree:

- **`teh-273`** — filter to suppress subharmonics *and* harmonics after a VHF transmitter.
  HRS marks **(d) niskopropusni**; RK (Skupina IV, pit. 52, tiskana str. 330) gives
  **(b) pojasnopropusni**, and RK's prose on str. 193 backs (b): a low-pass cannot touch a
  subharmonic, which sits in its pass band. *This one `strict.py` already reports* — it is one
  of the five known book-vs-HRS disagreements, so two independent methods agree.
- **`teh-261`** — interference persisting with the TV antenna disconnected. HRS marks
  **(c) zamjenom TV antenskog kabla**; RK (Skupina III, pit. 55, tiskana str. 319) gives
  **(d) ugradnjom mrežnog filtra**. **New** — outside `strict.py`'s verified id mapping, so it
  rests on the batch's own skupina/question alignment rather than on the cross-check.

Both answers are kept as HRS marks them, with the divergence stated in the note.

### The inherited citations were wrong at scale

Not the occasional slip recorded earlier — the norm. Examples:

- **teh 4 (Prijamnici): 16 of 17** questions cited `PZM 4. Prijamnici, str. 107–109`. Searching
  all of PZM: `drift` 0 hits, `AGC` 0 hits, `ratio detektor` 0 hits.
- **teh 1:** the Ohm's-law questions and the frequency questions had their citations *swapped*.
- **teh 5:** PZM never mentions amplifier classes A/AB/B/C, yet five questions cited it for them.
- **teh 7: 30 of 41** cited the same three pages; `MUF` does not appear anywhere in PZM.
- **teh 2:** PZM has no section on integrated circuits at all (`integrirani`, 0 hits).

The centre of gravity moved from PZM to RK throughout: PZM is written for the P exam, RK is the
A-class handbook. Every printed page cited in the new notes was read off the page.

### Wikipedia disambiguation pages answer HTTP 200

Six Croatian titles that "verified" fine are disambiguation pages teaching nothing: `Filtar`,
`Kondenzator`, `Zavojnica`, `Oscilator`, `Impedancija`, `Kirchhoffovi zakoni`. 22 links had
already shipped. `link_check.py` now queries the Wikipedia API's pageprops and fails on any of
them — scraping the HTML for "disambiguation" does **not** work, it false-positives on ordinary
articles. Replacements are in `build/work/LINKS.md`. Also: hr `Signal` is the messaging app.

### Book errors worth knowing (the books, not us)

- **RK's image-frequency formula, tiskana str. 135**, is wrong as printed: it gives
  `2·f_MF + f_LO`. The correct relation is `f_zrcalna = f_signala + 2·f_MF`.
- **RK's ch. 10 legal references are all dead** — Zakon NN 105/1999 and Pravilnik NN 183/04,
  both superseded (NN 91/10 + 114/18; NN 146/14 + 59/16 + 31/19, whose 2019 amendment
  *replaced* the numeric annexes). "Hrvatska agencija za telekomunikacije" is now HAKOM.
- **PZM str. 112** gives the AM power split as 50 % / 25 % / 25 %. At m = 100 % it is 2/3
  carrier and 1/6 per sideband.
- **RK's zbirka, tiskana str. 317, q42–43 are mutually inconsistent** (6 V peak read off a
  scope, then a power answer that only works if the 6 V is effective). RK's answer pages are
  scans with no text layer, so this cannot be checked automatically.
- **The exam key computes with √2 ≈ 1,41**, expecting 620,4 V where the exact value is 622,25 V.
  RK does the same in its own worked example, so the key is at least self-consistent.
- **The books disagree on earth resistance**: RK "a few ohms", PZM str. 131 "below 20 Ω".
- **RK and PZM disagree on ionospheric layer heights.** The notes follow RK, which the key does.

### Tooling added

- `build/booktool.py` — resolves printed pages. **`Radiokomunikacije.pdf` is a pure scan with
  no text layer**; the searchable twin is `Radiokomunikacije_ocr.pdf`, page-for-page identical.
  The folio map is derived by reading each page's own number, discarding impossible ones by
  requiring folios to increase, and filling gaps from the neighbouring offset. RK resolves in
  four regions: pdf 0–9 `+3`, 10–280 `+4`, 281–350 `+6`, 351–409 `+7` (0-based).
- `build/check_notes.py` — the merge gate: coverage, flags preserved, cite keys valid, printed
  pages real, links well-formed and unique, notes actually expanded.
- `build/link_check.py` — fetches every link and rejects disambiguation pages.
- `build/make_packets.py`, `build/work/` — per-topic work packets and the briefs.


---

## 5. Six figures were missing, not one — 9 August 2026 (later the same day)

Glaukon reported that `teh-024` had no picture. It has one. So did five other questions.

### The claim in §4 was wrong, and wrong for an instructive reason

§4 recorded that page 3 of the technical bank "carries no images and no vector drawings". That
was measured with `page.get_images()` and `page.get_drawings()`, and both really do return
empty — on a page that plainly shows a current node when you render it. The exam PDFs come out
of **PrimoPDF**, which draws line art as a swarm of **inline images**: `BI /W 236 /H 1 ... ID
... EI`, 949 of them on page 3 alone, each one pixel high. `get_images()` documents that it
does not report inline images; `get_drawings()` sees no paths because there are none. Two APIs
agreed, and both were answering a different question than the one being asked.

**The lesson is not about PyMuPDF.** Two independent-looking checks that share one assumption
are one check. The cheap disconfirmation — render the page and look at it — was never run,
because the two agreeing APIs felt like corroboration.

### The gate, not the crop, was the defect

`figures2.py` only ever *attempted* a crop when the stem said "slika", "shema", "crtež"… Six
questions show a drawing and never mention it: *"Izračunaj vrijednost struje I3!"* is a bare
imperative under a node diagram. The keyword list had been growing a hand-maintained escape
hatch (`FORCE_FIGURE`) for exactly this, one id at a time.

Replaced with a measurement. `nontext_ink()` renders the band below a question's options,
paints every **character** white, and counts what survives. Masking at line or span level does
not work: the figure labels sit on baselines padded with dozens of leading spaces, whose bboxes
cover the drawing — that mask reported `teh-112`'s spectrum as blank paper. The separation is
absolute, not a tuned threshold:

| | non-text ink in the band |
| --- | --- |
| every text-only question | **0** |
| the six missed figures | 1019 – 3300 |

Measured **below the options only**. `teh-017` and `teh-081` carry a formula as an image inside
the *stem* — already transcribed into text by `overrides.json` — and must not be re-shown as a
picture of themselves.

**Found: `teh-024`, `teh-041`, `teh-042`, `teh-046`, `teh-112`, `teh-277`.** 46 figures → **52**.

### Two answer-leaks fixed on the way

Picking between the two candidate bands used *total* ink, and the whole-question band always
wins on total ink because it contains the stem and options. `teh-277` — four wordy options
under a modest antenna sketch — therefore shipped **a picture of its own question**. Red is
neutralised inside the crop, but HRS types the marked option in a different typeface, so the
answer was still legible. `teh-186` did the same for a different reason: the `e)`–`h)` options
of the unnumbered `teh-186b` had pushed its "last option line" past its own polar plot.

Both now select by **drawing** ink (`≥ 0.6` of the best band), and the unnumbered-question
handler now clamps the preceding question's option line as well as its extent.

### Three questions whose options had eaten the figure's labels

Same defect class as `teh-258`, and only visible now that the figures are displayed:

| id | option | was | is |
| --- | --- | --- | --- |
| `teh-046` | b | `1 uH, L1 L2 R L3` | `1 uH` |
| `teh-112` | b | `amplitudne modulacije, fc= frekvencija vala nositelja …` | `amplitudne modulacije` |
| `teh-277` | d | `…nikada nema pozitivne učinke. AP prema odašiljaču…` | `…nikada nema pozitivne učinke.` |

All three read off the rendered page and recorded in `overrides.json`.

### `teh-024` answered from its own figure

The diagram: four branches at one node, **I4 = 5 A in**, **I1 = 3 A out**, **I2 = 2 A out**,
I3 out and unknown. 5 − 3 − 2 = **0 A**, which is exactly what HRS marks in red (c). The note
now works the real numbers, and each wrong option is accounted for: 5 A is I4 with a branch
forgotten, 1 A is I1 − I2 with the inflow forgotten, −5 A is the sign slip.

The crop also picked up a stray folio digit on any figure that ran to the foot of a page
(`teh-041` shipped with a "5", `teh-074` with an "11"); bands are now clamped above the page
number.

`strict.py` moved 102/107 → **103/108** — the cleaned option text let one more book question
match.
