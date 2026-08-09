# Adjudicate prv-057 and teh-261 with the club

prio:       P2
cluster:    key-disputes
files:      quiz/build/overrides.json, quiz/REVIEW.md
blocked-by: club ruling — Glaukon to ask

**Why.** Two questions where the HRS key looks wrong rather than merely outdated, which is
past the line rule 1 draws. `prv-057`: the key gives the locator field as 10° longitude ×
20° latitude, but Maidenhead is the reverse, and 18 × 20° = 360° settles it. `teh-261`: HRS
marks "replace the TV antenna cable" while RK's own table marks "fit a mains filter"; it
falls outside `strict.py`'s verified mapping, so neither source checks the other.

**Done when.** The club has ruled on both, the ruling is recorded in REVIEW.md with its
date and who gave it, and the quiz reflects it — including leaving the key untouched if
that is the ruling.

**Avoid.** Do not change either answer before the ruling, however clear the physics looks.
Rule 1 exists for exactly this case: the exam marks HRS's key, not the truth.
