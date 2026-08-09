# Pre-verified link catalogue

Every entry below was fetched on 9 August 2026 and returned HTTP 200. Use them freely
**without re-fetching** — that is the point of this file. Anything *not* on either list still
has to be confirmed yourself (rule 2), and when you confirm one, add it here.

Base for the first list: `https://hr.wikipedia.org/wiki/<Title>` with spaces as `_` and
diacritics percent-encoded by the URL, e.g.
`https://hr.wikipedia.org/wiki/Elektri%C4%8Dna_struja`.

## hr.wikipedia — DISAMBIGUATION PAGES, never link these

They answer HTTP 200, so fetching them "confirms" nothing — but they are just lists of
meanings and teach the reader nothing. Six shipped in the notes before this was caught.
Use the replacement instead:

| Do not link | Use instead |
| --- | --- |
| hr `Filtar` | en `Electronic_filter` |
| hr `Kondenzator` | hr `Električni_kondenzator` |
| hr `Zavojnica` | hr `Električni_induktivitet` |
| hr `Oscilator` | hr `Oscilator_(elektrotehnika)` |
| hr `Impedancija` | hr `Električna_impedancija` |
| hr `Kirchhoffovi zakoni` | en `Kirchhoff's_circuit_laws` |
| en `Modulation_index` | en `Amplitude_modulation` or `Frequency_deviation` |

Also: **hr `Signal` is about the messaging app**, not about signals — use en `Signal`.

`python link_check.py` now queries the Wikipedia API's pageprops and fails the build on any
disambiguation link, so you do not have to spot these by eye — but do not add one knowingly.

## hr.wikipedia — CONFIRMED TO EXIST

Akumulator · Amper · Amplitudna modulacija · Anoda · Antena · Baterija · Decibel · Dielektrik · Dioda · Dipol · Električna struja · Električni napon · Električni otpor ·
Električno polje · Elektromagnetski val · Elektromagnetsko zračenje · Elektronska cijev ·
Farad · Filtar · Frekvencija · Frekvencijska modulacija · Gromobran · Herc · Impedancija ·
Induktivitet · Integrirani krug · Ionosfera · Ispravljač · Istosmjerna struja · Izmjenična
struja · Izolator · Kapacitet · Katoda · Kirchhoffovi zakoni · Koaksijalni kabel · Kondenzator ·
Logaritam · Logička vrata · Magnetsko polje · Modulacija · Morseov kod · Multimetar · Napon ·
Njihalo · Ohm · Ohmov zakon · Operacijsko pojačalo · Oscilator · Osciloskop · Osigurač · Otpor ·
Otpornik · Pojačalo · Poluvodič · Rad (fizika) · Radioamaterizam · Radiodifuzija · Radiotehnika ·
Radioteleskop · Radiovalovi · Rezonancija · Snaga · Stojni val · Struja · Strujni udar ·
Titrajni krug · Titranje · Transformator · Tranzistor · Uzemljenje · Val · Valna duljina ·
Vodič · Volt · Watt · Zavojnica · Zener dioda · Zvuk

(Remove the bogus "Batterija" entry if you see it — it is a typo, not an article.)

## hr.wikipedia — CONFIRMED **NOT** TO EXIST (404 — do not link, do not re-check)

Antenski vod · Efektivna vrijednost · Elektromagnetska kompatibilnost · Elektromagnetska
smetnja · Feritna jezgra · Frekvencijski pojas · Henri (jedinica) · Kratki val · Kratki valovi ·
Kristalni oscilator · Poluvalni dipol · Prizemni val · Prostorni val · Reaktancija · Sinusoida ·
Snaga (fizika) · Superheterodin · Superheterodinski prijamnik · Tesla (jedinica) ·
Ultrakratki valovi · Yagi-Uda antena

For every one of those, go to en.wikipedia instead (`Reactance`, `Superheterodyne receiver`,
`Yagi–Uda antenna` — note the en dash, percent-encoded as `%E2%80%93` — `Ground wave`,
`Skywave`, `High frequency`, `Very high frequency`, `Electromagnetic compatibility`,
`Ferrite core`, `Crystal oscillator`, `Dipole antenna`, `Root mean square`, `Henry (unit)`,
`Tesla (unit)`, `Sine wave`), and label it so Glaukon knows it is in English:
`{"label": "Reactance (en.wikipedia)", "url": "https://en.wikipedia.org/wiki/Electrical_reactance"}`.

## en.wikipedia — already used and confirmed in the worked example

Decibel · Effective radiated power · Radiation pattern · Side lobe · S meter · Coaxial cable ·
Yagi–Uda antenna (`Yagi%E2%80%93Uda_antenna`)

## Legal sources

Link the Narodne novine text directly rather than a summary:

- [Pravilnik NN 150/2022](https://narodne-novine.nn.hr/clanci/sluzbeni/2022_12_150_2313.html)
- [Zakon o elektroničkim komunikacijama NN 76/2022](https://narodne-novine.nn.hr/clanci/sluzbeni/2022_07_76_1116.html)
  — note **1116**, not 1113. `...76_1113.html` is a different act in the same issue and serves
  only Narodne novine boilerplate with no law text. The wrong one was in circulation here.

Both confirmed. HAKOM and the ITU/IARU sites are fine too, but fetch before you link — HAKOM
reorganises its site often and old deep links rot.

For anything about band segments and which mode goes where, the authority is the IARU plan,
not the Pravilnik — NN 150/22 regulates only band edges and maximum bandwidth, never mode
segmentation (the sole exception is Napomena 3, 10 100–10 150 kHz). Both confirmed:

- [IARU R1 HF band plan (PDF)](https://www.iaru-r1.org/wp-content/uploads/2019/08/hf_r1_bandplan.pdf)
- [IARU R1 band plans (index)](https://www.iaru-r1.org/reference/band-plans/)

Note the `/2019/08/` path — the `/2021/03/` one linked from the newer page is a 404.

## en.wikipedia — confirmed by batch teh3_krugovi_a (circuit theory)

All fetched 9 Aug 2026, HTTP 200, and checked that the article really covers the point.
Base `https://en.wikipedia.org/wiki/<Title>`:

`Electronic_filter` · `Low-pass_filter` · `High-pass_filter` · `Band-stop_filter` ·
`LC_circuit` · `RC_circuit` · `Q_factor` · `Rectifier` · `Diode_bridge` (Graetz bridge) ·
`Voltage_regulator` · `Harmonic` · `Frequency_multiplier` · `Frequency_mixer` ·
`Power_amplifier_classes` (covers A / AB / B / C) ·
`Shannon%E2%80%93Hartley_theorem` (en dash!) · `Amplitude_modulation` ·
`Single-sideband_modulation` · `Frequency_deviation` · `Phase_modulation` ·
`Continuous_wave` · `Voltage-controlled_oscillator` · `Phase-locked_loop` · `Phase_noise`

**Do NOT use** `Modulation_index` — the page exists but is only a disambiguation stub with no
definitions. Use `Amplitude_modulation` (AM depth) or `Frequency_deviation` (FM) instead.
`Phase_noise` exists and is good on phase noise, but says nothing about *amplitude* noise —
link it only as the contrasting concept, not as a source for amplitude noise.
