# Resolve the five strict.py book-vs-HRS disagreements

prio:       P2
cluster:    key-disputes
files:      quiz/build/strict.py, quiz/REVIEW.md, quiz/build/overrides.json
blocked-by:

**Why.** `teh-201`, `teh-273`, `pro-090`, `pro-047` and `prv-009` are the residue holding
the cross-check at 95.4 %. They are documented in REVIEW.md §2–4 and have not moved since.
Each is either a real key conflict worth flagging in the UI or a mapping artefact worth
fixing in `strict.py` — and nobody currently knows which.

**Done when.** Each of the five is classified as *flag* (surfaced in the quiz like the other
conflicts) or *mapping bug* (fixed, and `strict.py` rises accordingly), with the reasoning
in REVIEW.md. A residual disagreement is an acceptable outcome if it is explained.

**Avoid.** `pro-047` already carries a `conflict` flag — do not double-flag it or drop the
existing warning prose. Do not raise the strict.py percentage by loosening the check.
