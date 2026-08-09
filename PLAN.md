# Plan: Croatian Amateur Radio Licence (A class) → Pico Balloons

**Target:** A-class licence (HAREC / CEPT T/R 61-01), then WSPR pico balloon flights
**Plan written:** 7 August 2026

---

## Decision: sit the **A** exam, not P

P is not a prerequisite for A (Pravilnik čl. 5. st. 1. — you sit the exam for A *or* P directly),
and there is no shortcut upgrade later: passing P and then wanting A means sitting the full A exam anyway.

| | **P (početnički)** | **A** |
|---|---|---|
| Exam structure | 20 tech + 20 regs + 20 procedures | **40** tech + 20 regs + 20 procedures |
| Duration | 30 + 30 + 30 min | 45 + 30 + 30 min |
| Pass mark | 60% **in each** of 3 areas | 70% **in each** of 3 areas |
| Fee | free | **€30** (retake €11) |
| Published question bank | ~225 tech / ~87 regs / ~63 proc | ~290 tech / ~95 regs / ~79 proc |
| Max power | 100 W PEP | 1500 W PEP |
| International recognition | CEPT Novice, ECC/REC/(05)06 | **HAREC + CEPT T/R 61-01** (~40 countries) |

**Why A:**

1. **The extra work is marginal.** P's syllabus is a strict subset of A's. Comparing section IV
   (P) against section II (A) of `docs/Obvezni_dio_ispitnog_programa.pdf`, P merely omits
   Kirchhoff's laws, PLL, DSP, receiver/transmitter stage detail and propagation depth.
   The A technical bank is only ~65 questions larger.
2. **HAREC is the real prize** (čl. 12. st. 5.). P gets only ECC/REC/(05)06, honoured by far
   fewer administrations.
3. **€30 once beats €30 later** plus a second round of study.
4. **Band clarity for pico work** — see below.

### Band check for pico balloons (Dodatak 1, Tablica 1)

P class HF is: 3500–3800, 7000–7200, **14040–14150**, **14280–14350**, 21000–21450,
28000–29700 kHz @ 100 W.

The two mainstream pico WSPR bands *would* fit under P:

- 20 m WSPR — RF 14.0970–14.0972 MHz → inside P's 14040–14150 ✔
- 10 m WSPR — RF 28.1260–28.1262 MHz → inside P's 28000–29700 ✔

But P's 20 m is split into two islands, and **30 m (10100–10150 kHz) is A-only** — and even for A
it is restricted to A1A/F1B emissions (Napomena 3). A removes all sub-band arithmetic.

---

## ⚠️ The pico balloon regulatory problem — resolve this BEFORE building

**The Pravilnik (NN 150/22) has no category that fits a free-flying unattended transmitter.**
It is not explicitly prohibited (unlike the UK, which bans airborne amateur operation outright),
but it is not provided for either.

- **čl. 4. st. 3.** enumerates the permitted station types. A free-flying beacon fits none of them.
- A **radiofar** (čl. 4. st. 3. t. 4.) may only be established by the Savez or a **club**, needs a
  *separate* licence (**čl. 12. st. 9.**), must name a responsible operator (**čl. 12. st. 10.**),
  and **must operate at the location and on the frequencies stated in the licence**
  (**čl. 14. st. 5.**). A balloon has no fixed location.
- **čl. 13. st. 1.** permits mobile operation *"u motornom vozilu, na plovilu ili zrakoplovu uz
  prethodno odobrenje zapovjednika"* — prior approval of the craft's **commander**. This presupposes
  a crewed craft with the operator aboard. A free balloon has no commander.

**Action: get a written answer from HAKOM.** Draft prepared — see `emails/02_HAKOM_upit_zracni_rad.md`.

### Three further requirements that bite a homebuilt tracker

| Article | Requirement | Consequence |
|---|---|---|
| **čl. 12. st. 3.** | Homebuilt stations (*samogradnja*) need an *uvjerenje o tehničkoj sukladnosti* issued by HRS | A self-assembled Traquito Jetpack / QRP Labs U4B falls under this. Budget time. |
| **čl. 15. st. 3.** | Callsign transmitted at least every 10 minutes | WSPR encodes the callsign in every message — a 10-min TX schedule satisfies this |
| **čl. 20.** | Station log must be kept, retained 12 months | Periodic export from wspr.live / the WSPR database is your log |

Also useful: **čl. 12. st. 2.** — stations with **ERP ≥ 100 W** trigger an extra EMF documentation
tier. Pico payloads run 10–25 mW, three orders of magnitude below, so this never applies.

### Separate track: aviation

The balloon itself is governed by **HACZ** (Hrvatska agencija za civilno zrakoplovstvo), *not* HAKOM.
Jakovlje sits under Zagreb terminal airspace. **A radio licence does not cover the flight.**
This was not researched and must be treated as an independent approval track.

---

## Club

There is **no radio club in Jakovlje or Zaprešić.** Nearest options:

| Club | Callsign | Location | Distance from Jakovlje |
|---|---|---|---|
| Radio klub grada Zaboka | 9A1CAZ / 9A0Z | Kumrovečka 4, Zabok | ~15 km N |
| Radio klub "Stubica" | 9A1CBO / 9A2S | Donja Stubica | ~20 km NE |
| Radio klub Samobor | 9A1BIJ / 9A1W | Samobor | ~25 km SW |
| **ZARS clubs** (RK Zagreb 9A1ADE, RK Tehničar, HDXK 9A1A, RK FER, RK Dubrava, RK Veza, 9A1WFF) | various | Bulićeva 14, Zagreb | ~25–30 km SE |

**Recommendation: join a ZARS club in Zagreb** — RK FER or Radio klub Zagreb (9A1ADE) first choice.

- ZARS is the only organisation with a **documented, scheduled A/P course**: weekly, Monday
  evenings, Bulićeva 14, roughly €20 (+€30 for A candidates).
- Pico ballooning needs HF, digital modes, antennas and homebrew people — the Zagreb technical clubs.
- čl. 12. st. 3. means HRS must certify your homebuilt tracker. Being embedded in a Zagreb club
  with people who have done that is worth the drive.
- Zabok is closer but shows no evidence of running courses; its site's last visible activity is 2021.

**Pragmatic combination:** Zagreb club for course + exam + technical network; keep contact with
Zabok or Stubica for local antenna help and a nearby club station.

Club membership is *not* legally required to sit the exam (čl. 9. st. 1. — apply directly to HRS
or to a club), but in practice exams are organised through clubs.

---

## Timeline

| When | What |
|---|---|
| **Mon 17 Aug 2026** | HRS office reopens (closed 27 Jul – 14 Aug). Send all three emails. |
| **24 Aug – 13 Sep** (3 wks) | Textbook + Pravilnik |
| **14 Sep – 4 Oct** (3 wks) | Grind the three A question banks |
| **5–11 Oct** | Procedures rote learning + mock tests |
| **Mid/late Oct 2026** | Sit A exam |
| **Nov 2026** | PPO from HRS → HAKOM e-Amaterska → licence issued |
| **Winter 2026/27** | Build tracker + receive station; obtain *uvjerenje o tehničkoj sukladnosti* |
| **Spring 2027** | First flight (longer daylight favours solar payloads) |

**Lead times are the binding constraint:** the club must file with HRS **30 days** before the exam
(čl. 8. st. 3.), and HRS notifies HAKOM **15 days** before (čl. 6. st. 1.). Decision → sitting is
realistically 6–8 weeks. Apply by **early September** to make a mid-October exam.

---

## Study plan

Everything needed is already in `docs/`. Work in this order:

### 1. `docs/Pasaric_Radioamaterizam_za_mlade.pdf` (214 pp) — 1 week
The free HRS textbook. Read once end to end. Don't over-invest — it's written for beginners
and the electronics will be familiar.

### 2. `docs/Pravilnik_o_amaterskim_radijskim_komunikacijama_NN_150_22.pdf` — 2 weeks, read twice
**Highest-yield document in the workspace.** Directly supplies the answers to the 20 *propisi*
questions, and 70% per section means you cannot be weak here.

Memorise: **Dodatak 1, Tablica 1** (bands, power, P/Pex/S status per class) and all **Napomene 1–7**.

### 3. The three A-class question banks — 3 weeks, ~25/day
- `docs/RA_ispiti_9_A_razred_Tehnicki_dio.pdf` (~290 q)
- `docs/RA_ispiti_8_A_razred_HR_i_medjunarodni_propisi.pdf` (~95 q)
- `docs/RA_ispiti_7_A_razred_Pravila_i_postupci.pdf` (~79 q)

Per the HRS *Odluka* (`docs/RA_ispiti_1_Odluka_o_provodjenju_ispita.pdf`, t. 12), clubs *may*
choose other questions, but in practice draw from these lists.

### 4. Procedures — rote, 1 week
Phonetic alphabet, Q-codes, operating abbreviations, IARU bandplans. The cheapest 20 questions
on the exam and pure memorisation.

### Skip / skim
- `docs/CEPT_Preporuka_TR61_02.pdf` and `docs/ERCRep32.pdf` — these are the *source* of the
  syllabus, not exam content.
- `docs/CEPT_preporuka_TR61_01.pdf` — read lightly; it's what your A licence will be issued under.
- The P-class banks (`RA_ispiti_10/11/12`) — subset of A, no extra value.
- `docs/HAKOM_Dopunsko_rjesenje_P_razred.pdf` and `RA_ispiti_2` — just lists of appointed examiners.

---

## Exam & licence mechanics

**Application** (čl. 9. st. 1.): written request to HRS or your club containing *ime i prezime,
OIB, razred (**A**)*. Pay €30 to HRS.

**Exam:** written multiple-choice (čl. 8. of the Odluka). **70% in each** of three sections.
Failing any one section means retaking **all three**, minimum **2-month** gap (čl. 10. st. 2.), €11.

**After passing:**
1. Request the **PPO** (*potvrda o prijedlogu pozivne oznake*) from HRS.
2. Apply to HAKOM via **e-Amaterska**: https://app.hakom.hr/default.aspx?id=10787
   Attach: PPO, *svjedodžba* (exam certificate), OIB document, station/equipment details.
   Licences issued electronically since 1 Jan 2024.
3. Callsign format (čl. 15. st. 1.): `9A` + one digit + up to three letters.
4. Report any change of address or equipment to HAKOM within **15 days** (čl. 12. st. 16./17.).

---

## Pico balloon resources

- **https://traquito.github.io/** — best current resource. Jetpack tracker ~$14 shipped,
  WSPR on 20 m, solar, full build guides and live map. **Start here.**
- **https://github.com/EngineerGuy314/pico-WSPRer** — RP2040-based, if building from source.
- **QRP Labs U4B** — the other mainstream tracker.
- **https://www.picoballoonarchive.org/** — flight histories; what actually survives.

**Sequencing: receive before you transmit.** Set up a WSPR receive station at home first —
no licence needed to listen (**čl. 12. st. 7.** — receive-only stations need no licence), it
teaches you the ecosystem, and it earns credibility in the club. An RTL-SDR plus a 20 m dipole
is enough.

---

## Open questions

| Question | Who answers | Status |
|---|---|---|
| Is unattended airborne operation permitted? Under what station category? | HAKOM | Email drafted |
| Annual HAKOM spectrum fee for an amateur licence (€/yr) | HAKOM | **Unknown — not published anywhere I could find** |
| HRS 2026 exam calendar | HRS | Not published; phone call needed |
| Does ZARS's autumn A course run in 2026? | ZARS | Email drafted |
| Croatian aviation rules for free balloons | HACZ | **Not researched — separate track** |
| Do Zabok / Stubica run courses? | those clubs | Web presence stale |

---

## Contacts

| Organisation | Contact |
|---|---|
| **HRS** (Hrvatski radioamaterski savez) | Dalmatinska 12/3, 10000 Zagreb · radioamateri@hamradio.hr · +385 1 48 48 759 |
| **ZARS** (Zagrebački radioamaterski savez) | Bulićeva 14, Zagreb · zagrebacki.radioamaterski.savez@zg.t-com.hr |
| **HAKOM** | R. F. Mihanovića 9, 10110 Zagreb · ZahtjevZaDozvolu@hakom.hr · +385 1 7007 007 |
| **e-Amaterska portal** | https://app.hakom.hr/default.aspx?id=10787 |
| Radio klub grada Zaboka | Kumrovečka 4, 49210 Zabok · https://www.9a0z.com/ |
| Radio klub Zagreb 9A1ADE | https://www.rkz.hr/ |

## Reference links

- HRS — Kako postati radioamater: https://www.hamradio.hr/kako-postati-radioamater/
- HRS — Kako do radioamaterske dozvole: https://www.hamradio.hr/kako-do-radioamaterske-dozvole/
- Pravilnik NN 150/2022: https://narodne-novine.nn.hr/clanci/sluzbeni/2022_12_150_2313.html
- HAKOM — Amaterske radijske postaje: https://www.hakom.hr/hr/amaterske-radijske-postaje/3363
- Croatian club directory (9A3AL): http://www.9a3al.com.hr/LINKOVIHRVATSKA.html
- UKHAS — airborne amateur legislation by country: https://ukhas.org.uk/doku.php?id=general:aprs_legislation
