# Trim stray diagram labels from teh-137 option d

prio:       P2
cluster:    build-pipeline
files:      quiz/build/overrides.json, quiz/build/bank.json
blocked-by:

**Why.** `teh-137` (HRS-A, RA_ispiti_9_A_razred_Tehnicki_dio.pdf, pitanje 137, str. 19) option d)
reads "PLL sintezator. Δf fref f0 = fref fazni NPF VCO detektor PLL programibilni djeljitalj" —
the correct answer text followed by OCR-scraped block-diagram labels from sl. 3.6.4. (RK
3.6.2., tiskana str. 126–127), same bug pattern already patched for `teh-186`, `teh-258` and
`teh-046` in overrides.json ("stray fragments from the adjacent figure/schematic appended to
an option"). It should just say "PLL sintezator".

**Done when.** `overrides.json` has a `teh-137` patch entry setting `options.d` to "PLL
sintezator" (or the exact wording confirmed against the rendered PDF page 19), with a `reason`
following the existing entries' style; a rebuild picks it up and the quiz app shows the
trimmed option.

**Avoid.** Don't touch the `teh-137` note in `quiz/build/notes_zzz_expanded_teh3_krugovi_a.json`
— it already correctly describes the PLL block diagram and cites `teh-135`/`teh-136`; the bug is
only in the option text pulled into `bank.json` from the raw parse. Don't change the `answer`
or `red_marks` (still "d").
