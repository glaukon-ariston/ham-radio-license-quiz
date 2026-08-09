# Brief — expanding the teaching notes

You are writing the study notes for one batch of a Croatian A-class amateur-radio exam quiz.
Glaukon is preparing for the real exam. He asked for **longer, less terse explanations**: real
prose that explains the *why*, the maths written out where it applies, external links for
further study, and a reference to the section in the local books.

## Your input and your output

Your packet is `quiz/build/work/packet_<name>.json`. It holds every question you own, with its
options, the authoritative answer, the current (terse) explanation, the current citation, and a
`flag` if the question is one of the 32 with a known legal conflict.

Write **one file**: `quiz/build/notes_zzz_expanded_<name>.json`. Cover **every** id in your
packet — no skipping. `rebuild.py` applies `notes_*.json` in sorted order and the last file
wins, so the `zzz_expanded_` prefix is what makes your notes override the terse originals.

```json
{
  "_doc": "what this batch covers",
  "teh-032": {
    "note": "Paragraphs separated by a blank line. Croatian. Explain the WHY, not just the what.",
    "formula": ["L = 10 · log₁₀(P₂/P₁)   [dB]", "", "Provjera: 5 W + 10 dB → 50 W"],
    "links": [{"label": "Decibel (hr.wikipedia)", "url": "https://hr.wikipedia.org/wiki/Decibel"}],
    "cite": [{"src": "RK", "loc": "1.9.4. O decibelu (dB), tiskana str. 53–55"}]
  }
}
```

- `note` — **required**, Croatian. `\n\n` starts a new paragraph. Aim for 2–4 paragraphs:
  what the answer is and why it follows; the mechanism or the reasoning behind it; a practical
  consequence, a common trap, or how it connects to another question (`vidi teh-179`).
  Address the reader as *ti*, the way the worked example does.
- `formula` — optional list of lines, rendered as a monospace block; `""` gives a blank line.
  Use it wherever there is arithmetic, a unit relation, a band edge, a table worth memorising,
  or a rule of thumb. Show the substitution, not just the symbols.
- `links` — optional but wanted. **See rule 2.**
- `cite` — `src` must be one of: `NN150/22`, `RK`, `PZM`, `ODLUKA`, `OBVEZNI`, `TR61-01`,
  `TR61-02`, `ERC32`, `HRS-A`, `ZEK`. **See rules 3 and 5.**
- `flag` — only for legal conflicts. **See rule 4.**

The worked example of the target style is `quiz/build/notes_zzz_expanded_db.json` (13 questions,
the decibel family). Read it before you start. Match its depth and its voice.

## Rules that must not be broken

1. **Never change the HRS answer.** It is authoritative for what the examiner marks. Where the
   law disagrees with it, say so in the note and flag it — but the answer stays as it is, and
   your note must still explain why the examiner's key says what it says.
2. **Every external link must be fetched and confirmed** before it goes in. Read
   `quiz/build/work/LINKS.md` first: it lists Croatian Wikipedia articles already confirmed to
   exist and, just as usefully, the ones confirmed **not** to exist. Anything on the confirmed
   list you may use without re-fetching; anything else you fetch with WebFetch —
   that the page exists *and* that it actually covers the point. Croatian Wikipedia coverage is
   patchy; do not assume an article exists because the English one does. Prefer hr.wikipedia,
   fall back to en.wikipedia, and for legal questions link the Narodne novine text. A question
   with no good link gets no `links` key; that is fine and better than a dead one.
3. **Verify every printed page number against the page itself.** Use the helper:
   ```
   cd quiz/build
   python booktool.py map RK              # printed-page offset map (it is NOT constant)
   python booktool.py find RK decibel     # pages matching a term, with printed numbers
   python booktool.py page RK 53          # dump one printed page
   python booktool.py toc RK              # section headings
   ```
   Books: `RK` (Radiokomunikacije, HRS handbook — the scanned original has no text layer, so
   the tool reads the OCR'd twin, which is page-for-page identical), `PZM` (Pašarić,
   *Radioamaterizam za mlade*), and the legal sources `NN150/22`, `ODLUKA`, `OBVEZNI`,
   `TR61-01`, `TR61-02`, `ERC32`. RK's text is OCR, so it is noisy — read for sense, and never
   quote OCR mangling as if it were the book's wording. The existing citations are **not** all
   trustworthy: `teh-032` cited "PZM, decibel, str. 126", but that page is about spurious
   emissions and PZM has no decibel section at all. Re-check the citation you inherit; correct
   it when it is wrong.
4. **Preserve existing flags.** If your packet gives a question a `flag`, that question is one
   of the 32 the currency audit found where the exam key diverges from current law. Read its
   `current_explanation`, keep the warning in your new prose, and repeat the `flag` value
   verbatim in your output. Losing a flag is a real regression.
5. **Do not invent an article number or a page.** If you cannot verify it, say so in the note
   and cite nothing rather than citing something plausible. A wrong citation is worse than none
   — Glaukon will look it up.
6. Extract PDFs with **PyMuPDF**, never `pdftotext` — the latter destroys Croatian diacritics.
   Set `PYTHONIOENCODING=utf-8` before any Python that prints Croatian to a console.

## Croatian conventions used throughout

Decimal comma (`1,5 V`), `·` for multiplication, `→` for "becomes", Unicode sub/superscripts
(`P₂`, `10⁻³`, `log₁₀`), en dash in page ranges (`str. 53–55`), `tiskana str.` for a printed
book page. Croatian technical vocabulary: *odašiljač/predajnik*, *prijamnik*, *napojni vod*,
*valna duljina*, *titrajni krug*, *pojačalo*, *ispravljač*, *zavojnica*, *kondenzator*.

## When you are done

Validate your own file before reporting:

```bash
cd "g:/My Drive/Electronics/HAM Radio License"
PYTHONIOENCODING=utf-8 python -c "
import json
p=json.load(open('quiz/build/work/packet_<name>.json',encoding='utf-8'))['questions']
n=json.load(open('quiz/build/notes_zzz_expanded_<name>.json',encoding='utf-8'))
ids={k for k in n if not k.startswith('_')}
assert ids=={*p}, ('missing:',{*p}-ids,'extra:',ids-{*p})
SRC={'NN150/22','RK','PZM','ODLUKA','OBVEZNI','TR61-01','TR61-02','ERC32','HRS-A','ZEK'}
for k,v in n.items():
    if k.startswith('_'): continue
    assert v['note'].strip(), k
    assert all(c['src'] in SRC for c in v.get('cite',[])), k
    assert all(l['url'].startswith('http') for l in v.get('links',[])), k
    assert (p[k]['flag'] is None) or v.get('flag')==p[k]['flag'], ('flag lost',k)
print('ok',len(ids))
"
```

Do **not** run `rebuild.py` — the main conversation runs it once after merging every batch.

Report back: how many questions you wrote, which citations you had to correct, any link you
wanted but could not verify, and anything you found that Glaukon should know (a question whose
key looks wrong, a book section that contradicts another).
