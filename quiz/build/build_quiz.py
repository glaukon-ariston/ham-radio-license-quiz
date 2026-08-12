"""Build the self-contained quiz page from questions.json."""
import json
from pathlib import Path

# Resolved from this file, not cwd — rebuild.py runs us with cwd=quiz/build, but a direct
# `python quiz/build/build_quiz.py` from anywhere must still hit the same checkout's quiz/.
DST = Path(__file__).resolve().parent.parent
doc = json.loads((DST / "questions.json").read_text(encoding="utf-8"))
def pack(q, src):
    return {"id": q["id"], "s": q["section"], "sub": q.get("subsection"),
            "q": q["question"], "o": q["options"], "a": q["answer"], "src": src,
            # "f" is a path like "images/teh-024.png", relative to quiz.html itself — not a
            # base64 data URI. rebuild.py copies the PNG into quiz/images/ alongside
            # quiz.html; img.src resolves a relative path against the page's own location
            # under both file:// and http(s)://, so the runtime line below needs no change.
            "f": q.get("figure", {}).get("data"), "fo": bool(q.get("figure_is_options")),
            "e": q.get("explanation"), "flag": q.get("flag"),
            "fx": q.get("formula"), "lk": q.get("links"),
            "cs": q.get("cite_self"), "c": q.get("cite")}

live = [pack(q, "hrs") for q in doc["questions"]] +        [pack(q, "book") for q in doc.get("questions_extra", [])]
payload = json.dumps({"q": live, "meta": doc["_meta"], "src": doc["_sources"]},
                     ensure_ascii=False, separators=(",", ":"))

HTML = r"""<title>Radioamaterski ispit — A razred</title>
<style>
:root{
  --paper:#F4F6F6; --card:#FFFFFF; --ink:#14181A; --muted:#5B6B6E; --line:#D8DEDE;
  --accent:#0B5563; --accent-soft:#E3EDEF; --good:#2E7D53; --bad:#B3261E;
  --good-soft:#E4F1EA; --bad-soft:#F8E5E4; --warn:#8A5A00; --warn-soft:#FBF0D9; --shadow:0 1px 2px rgba(20,24,26,.07),0 8px 24px -12px rgba(20,24,26,.18); --fx-bg:#EEF2F2;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
}
@media (prefers-color-scheme:dark){:root{
  --paper:#0E1214; --card:#171D1F; --ink:#E8EDED; --muted:#93A3A6; --line:#2A3335;
  --accent:#38BEC9; --accent-soft:#123034; --good:#5FBF8B; --bad:#F2887F;
  --good-soft:#122A20; --bad-soft:#2E1A18; --warn:#E5B764; --warn-soft:#2C2413; --shadow:0 1px 2px rgba(0,0,0,.5),0 8px 24px -12px rgba(0,0,0,.7); --fx-bg:#101618;
}}
:root[data-theme="dark"]{
  --paper:#0E1214; --card:#171D1F; --ink:#E8EDED; --muted:#93A3A6; --line:#2A3335;
  --accent:#38BEC9; --accent-soft:#123034; --good:#5FBF8B; --bad:#F2887F;
  --good-soft:#122A20; --bad-soft:#2E1A18; --warn:#E5B764; --warn-soft:#2C2413; --shadow:0 1px 2px rgba(0,0,0,.5),0 8px 24px -12px rgba(0,0,0,.7); --fx-bg:#101618;
}
:root[data-theme="light"]{
  --paper:#F4F6F6; --card:#FFFFFF; --ink:#14181A; --muted:#5B6B6E; --line:#D8DEDE;
  --accent:#0B5563; --accent-soft:#E3EDEF; --good:#2E7D53; --bad:#B3261E;
  --good-soft:#E4F1EA; --bad-soft:#F8E5E4; --warn:#8A5A00; --warn-soft:#FBF0D9; --shadow:0 1px 2px rgba(20,24,26,.07),0 8px 24px -12px rgba(20,24,26,.18); --fx-bg:#EEF2F2;
}
/* "balanced" palette — indigo accent, warm-neutral grays. data-palette="muted" (or the
   attribute absent) falls through to the default :root block above, so only balanced and
   vivid need their own rules. Each palette repeats the same four-block shape as the muted
   one above (light default, prefers-color-scheme dark, then the two explicit data-theme
   overrides) so it composes with that light/dark mechanism instead of replacing it. */
:root[data-palette="balanced"]{
  --paper:#F5F4F7; --card:#FFFFFF; --ink:#17151F; --muted:#635B72; --line:#DAD5E0;
  --accent:#3D3AA8; --accent-soft:#E7E6F5; --good:#157A47; --bad:#C22A3E;
  --good-soft:#DFF3E7; --bad-soft:#FBE3E7; --warn:#92600A; --warn-soft:#FBEFD7; --shadow:0 1px 2px rgba(23,21,31,.07),0 8px 24px -12px rgba(23,21,31,.18); --fx-bg:#EFEDF5;
}
@media (prefers-color-scheme:dark){:root[data-palette="balanced"]{
  --paper:#131019; --card:#1C1826; --ink:#ECE9F2; --muted:#A79FBA; --line:#332C43;
  --accent:#8F8CF0; --accent-soft:#252043; --good:#6FD19B; --bad:#F28B95;
  --good-soft:#173327; --bad-soft:#3A1D22; --warn:#E8BE72; --warn-soft:#332811; --shadow:0 1px 2px rgba(0,0,0,.5),0 8px 24px -12px rgba(0,0,0,.7); --fx-bg:#171320;
}}
:root[data-palette="balanced"][data-theme="dark"]{
  --paper:#131019; --card:#1C1826; --ink:#ECE9F2; --muted:#A79FBA; --line:#332C43;
  --accent:#8F8CF0; --accent-soft:#252043; --good:#6FD19B; --bad:#F28B95;
  --good-soft:#173327; --bad-soft:#3A1D22; --warn:#E8BE72; --warn-soft:#332811; --shadow:0 1px 2px rgba(0,0,0,.5),0 8px 24px -12px rgba(0,0,0,.7); --fx-bg:#171320;
}
:root[data-palette="balanced"][data-theme="light"]{
  --paper:#F5F4F7; --card:#FFFFFF; --ink:#17151F; --muted:#635B72; --line:#DAD5E0;
  --accent:#3D3AA8; --accent-soft:#E7E6F5; --good:#157A47; --bad:#C22A3E;
  --good-soft:#DFF3E7; --bad-soft:#FBE3E7; --warn:#92600A; --warn-soft:#FBEFD7; --shadow:0 1px 2px rgba(23,21,31,.07),0 8px 24px -12px rgba(23,21,31,.18); --fx-bg:#EFEDF5;
}
/* "vivid" palette — violet accent, saturated good/bad/warn. Text-bearing pairs (good on
   good-soft, bad on bad-soft, warn on warn-soft, accent on card) are all >=4.5:1 contrast;
   verified with a WCAG contrast script before picking these hexes. */
:root[data-palette="vivid"]{
  --paper:#FBFAFF; --card:#FFFFFF; --ink:#0F1220; --muted:#5B5470; --line:#E1DCEF;
  --accent:#5B21B6; --accent-soft:#EFE3FB; --good:#087038; --bad:#C11229;
  --good-soft:#D8F5E3; --bad-soft:#FCDEE2; --warn:#924300; --warn-soft:#FDE8CC; --shadow:0 1px 2px rgba(15,18,32,.08),0 10px 28px -12px rgba(91,33,182,.25); --fx-bg:#F3EEFC;
}
@media (prefers-color-scheme:dark){:root[data-palette="vivid"]{
  --paper:#0B0812; --card:#18131F; --ink:#F5F1FC; --muted:#B7ABD4; --line:#362C49;
  --accent:#B98CFF; --accent-soft:#2C2145; --good:#38E28B; --bad:#FF6B7A;
  --good-soft:#0F3324; --bad-soft:#401B22; --warn:#FFC670; --warn-soft:#3A2A0C; --shadow:0 1px 2px rgba(0,0,0,.6),0 10px 28px -12px rgba(185,140,255,.35); --fx-bg:#140F1D;
}}
:root[data-palette="vivid"][data-theme="dark"]{
  --paper:#0B0812; --card:#18131F; --ink:#F5F1FC; --muted:#B7ABD4; --line:#362C49;
  --accent:#B98CFF; --accent-soft:#2C2145; --good:#38E28B; --bad:#FF6B7A;
  --good-soft:#0F3324; --bad-soft:#401B22; --warn:#FFC670; --warn-soft:#3A2A0C; --shadow:0 1px 2px rgba(0,0,0,.6),0 10px 28px -12px rgba(185,140,255,.35); --fx-bg:#140F1D;
}
:root[data-palette="vivid"][data-theme="light"]{
  --paper:#FBFAFF; --card:#FFFFFF; --ink:#0F1220; --muted:#5B5470; --line:#E1DCEF;
  --accent:#5B21B6; --accent-soft:#EFE3FB; --good:#087038; --bad:#C11229;
  --good-soft:#D8F5E3; --bad-soft:#FCDEE2; --warn:#924300; --warn-soft:#FDE8CC; --shadow:0 1px 2px rgba(15,18,32,.08),0 10px 28px -12px rgba(91,33,182,.25); --fx-bg:#F3EEFC;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  line-height:1.55;-webkit-text-size-adjust:100%}
.wrap{max-width:56rem;margin:0 auto;padding:0 1.1rem 4rem}
h1,h2,h3{text-wrap:balance;margin:0}
.eyebrow{font-family:var(--mono);font-size:.688rem;letter-spacing:.13em;text-transform:uppercase;color:var(--muted)}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}

header.bar{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--paper) 88%,transparent);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.barin{max-width:56rem;margin:0 auto;padding:.6rem 1.1rem;display:flex;align-items:center;gap:.9rem}
.brand{font-family:var(--mono);font-weight:700;letter-spacing:.04em;font-size:.94rem}
.brand span{color:var(--accent)}
.spacer{flex:1}
.tick{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:1rem;font-weight:700;
  padding:.16rem .5rem;border:1px solid var(--line);border-radius:.35rem}
.tick.warn{color:var(--bad);border-color:var(--bad)}
.themesel{font:inherit;font-size:.82rem;color:inherit;cursor:pointer;background:var(--card);
  border:1px solid var(--line);border-radius:.5rem;padding:.4rem .55rem}
.themesel:hover{border-color:var(--accent)}
.themesel:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

button{font:inherit;color:inherit;cursor:pointer}
.btn{background:var(--card);border:1px solid var(--line);border-radius:.5rem;padding:.5rem .85rem;
  box-shadow:var(--shadow)}
.btn:hover{border-color:var(--accent)}
/* --paper already inverts per theme, so it stays legible on --accent in both */
.btn.primary{background:var(--accent);color:var(--paper);border-color:var(--accent);font-weight:600}
.btn:focus-visible,.opt:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

.hero{padding:2.6rem 0 1.6rem;border-bottom:1px solid var(--line);margin-bottom:1.6rem}
.hero h1{font-size:clamp(1.6rem,4.5vw,2.3rem);letter-spacing:-.02em;line-height:1.12;margin:.5rem 0 .6rem}
.hero p{color:var(--muted);max-width:60ch;margin:0}

.modes{display:grid;gap:.9rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));margin:1.4rem 0 2rem}
.mode{background:var(--card);border:1px solid var(--line);border-radius:.7rem;padding:1rem 1.05rem;
  text-align:left;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:.4rem}
.mode:hover{border-color:var(--accent);transform:translateY(-1px)}
.mode h3{font-size:1.02rem}
.mode p{margin:0;color:var(--muted);font-size:.87rem}
.mode .spec{font-family:var(--mono);font-size:.72rem;color:var(--accent);letter-spacing:.04em}

.sect{margin:2rem 0 1rem;display:flex;align-items:baseline;gap:.7rem}
.sect h2{font-size:1.05rem;letter-spacing:-.01em}
.rule{flex:1;height:1px;background:var(--line)}

table{width:100%;border-collapse:collapse;font-size:.9rem}
.tscroll{overflow-x:auto}
th,td{text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--line)}
th{font-family:var(--mono);font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:600}
td.num{font-family:var(--mono);font-variant-numeric:tabular-nums;text-align:right}

/* S-meter style score bar with the 70% pass line marked */
.meter{position:relative;height:.62rem;background:var(--accent-soft);border-radius:.31rem}
.meter i{position:absolute;inset:0 auto 0 0;background:var(--accent);border-radius:.31rem}
.meter i.ok{background:var(--good)} .meter i.no{background:var(--bad)}
/* The pass line must read over the empty track and over either fill colour, in both themes:
   full-contrast ink with a paper-coloured halo, overhanging the bar top and bottom. The track
   deliberately does not clip (no overflow:hidden) — the fill rounds its own corners. */
.thr{position:absolute;top:-.45rem;bottom:-.45rem;width:3px;margin-left:-1.5px;
  background:var(--ink);border-radius:1.5px;box-shadow:0 0 0 1.5px var(--card)}

.qcard{background:var(--card);border:1px solid var(--line);border-radius:.7rem;padding:1.15rem 1.15rem 1.25rem;
  box-shadow:var(--shadow)}
.qhead{display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;margin-bottom:.7rem}
.qtext{font-size:1.06rem;line-height:1.45;margin:0 0 .9rem;text-wrap:pretty}
.fig{margin:0 0 1rem;background:#fff;border:1px solid var(--line);border-radius:.5rem;padding:.5rem;overflow-x:auto}
.fig img{display:block;max-width:100%;height:auto;margin:0 auto}
.opts{display:flex;flex-direction:column;gap:.5rem}
.opt{display:flex;gap:.7rem;align-items:flex-start;text-align:left;width:100%;
  background:var(--card);border:1px solid var(--line);border-radius:.5rem;padding:.7rem .8rem;line-height:1.45}
.opt:hover:not(:disabled){border-color:var(--accent);background:var(--accent-soft)}
.opt:disabled{cursor:default}
.opt .k{font-family:var(--mono);font-weight:700;color:var(--muted);flex:none;width:1.1rem}
.opt.sel{border-color:var(--accent);background:var(--accent-soft)}
.opt.ok{border-color:var(--good);background:var(--good-soft)} .opt.ok .k{color:var(--good)}
.opt.no{border-color:var(--bad);background:var(--bad-soft)} .opt.no .k{color:var(--bad)}
.verdict{margin-top:.9rem;font-size:.9rem;padding:.6rem .75rem;border-radius:.45rem;border:1px solid var(--line)}
.verdict.ok{border-color:var(--good);background:var(--good-soft)}
.verdict.no{border-color:var(--bad);background:var(--bad-soft)}
.nav{display:flex;gap:.6rem;align-items:center;margin-top:1.1rem;flex-wrap:wrap}
.hint{color:var(--muted);font-size:.78rem;font-family:var(--mono)}

.grid3{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(13rem,1fr))}
.stat{background:var(--card);border:1px solid var(--line);border-radius:.6rem;padding:.85rem .95rem;box-shadow:var(--shadow)}
.stat .big{font-family:var(--mono);font-size:1.75rem;font-weight:700;letter-spacing:-.02em;line-height:1.1}
.pill{font-family:var(--mono);font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;
  padding:.12rem .45rem;border-radius:.28rem;border:1px solid var(--line);color:var(--muted)}
.pill.ok{color:var(--good);border-color:var(--good)} .pill.no{color:var(--bad);border-color:var(--bad)}
.note{color:var(--muted);font-size:.84rem;max-width:64ch}
.why{margin-top:.85rem;padding:.7rem .8rem;border-left:3px solid var(--accent);
  background:var(--accent-soft);border-radius:0 .4rem .4rem 0;font-size:.9rem}
.why h4{font-family:var(--mono);font-size:.68rem;letter-spacing:.11em;text-transform:uppercase;
  color:var(--accent);margin:0 0 .3rem;font-weight:700}
.why.warn{border-left-color:var(--bad);background:var(--bad-soft)}
.why.warn h4{color:var(--bad)}
.why.check{border-left-color:var(--warn);background:var(--warn-soft)}
.why.check h4{color:var(--warn)}
.wp{margin:0 0 .55rem}
.wp:last-child{margin-bottom:0}
/* Worked maths sits apart from the prose: mono, indented, and allowed to scroll on its own
   so a long derivation never makes the page itself scroll sideways. */
.fx{font-family:var(--mono);font-size:.79rem;line-height:1.5;margin:.15rem 0 .5rem;
    padding:.4rem .6rem;border-left:2px solid var(--line);background:var(--fx-bg);
    overflow-x:auto;white-space:pre;color:var(--ink)}
.lk{margin-top:.6rem;font-size:.78rem;color:var(--muted)}
.lk a{color:var(--accent);text-decoration:none;border-bottom:1px solid transparent}
.lk a:hover,.lk a:focus-visible{border-bottom-color:var(--accent)}
/* .crumb: shared style for breadcrumb-style links — the in-quiz section/cjelina/home links
   in #qcrumb, and the top-of-screen home link on screens with no other breadcrumb content
   (picker, result). One rule so a home link looks identical wherever it appears. */
.crumb a{color:var(--accent);text-decoration:none;border-bottom:1px solid transparent}
.crumb a:hover,.crumb a:focus-visible{border-bottom-color:var(--accent)}
.cites{margin-top:.6rem;font-family:var(--mono);font-size:.72rem;color:var(--muted);
  line-height:1.5;border-top:1px dashed var(--line);padding-top:.5rem}
.cites b{color:var(--ink);font-weight:700}
.tag{font-family:var(--mono);font-size:.62rem;letter-spacing:.09em;text-transform:uppercase;
  padding:.1rem .35rem;border-radius:.25rem;border:1px solid var(--line);color:var(--muted)}
/* The question tag doubles as its permalink (#q=<id>) — right-click to copy the link. */
a.tag{text-decoration:none;color:var(--accent);border-color:var(--accent)}
a.tag:hover{background:var(--accent-soft)}
/* Tag lookup. On claude.ai the page runs in a cross-origin iframe, so a #q= fragment on the
   parent address never reaches us — this box is the route to a question that works there. */
.lookup{display:flex;flex-direction:column;gap:.35rem;margin:-.6rem 0 2rem}
.lookuprow{display:flex;gap:.5rem;flex-wrap:wrap;align-items:center}
.lookupin{font:inherit;font-family:var(--mono);color:inherit;background:var(--card);
  border:1px solid var(--line);border-radius:.5rem;padding:.5rem .7rem;flex:0 1 14rem;min-width:9rem}
.lookupin:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
/* In-page stand-in for window.confirm() — see the JS comment by askConfirm() for why. */
.confirm-mask{position:fixed;inset:0;z-index:30;background:rgba(20,24,26,.45);
  display:flex;align-items:center;justify-content:center;padding:1rem}
.confirm-box{background:var(--card);border:1px solid var(--line);border-radius:.7rem;
  padding:1.1rem 1.2rem;max-width:22rem;width:100%;box-shadow:var(--shadow)}
.confirm-box p{margin:0 0 1rem;font-size:.92rem;line-height:1.45}
.confirm-box .nav{margin-top:0}
.hidden{display:none!important}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
.mode,.opt,.btn{transition:border-color .12s ease,background .12s ease,transform .12s ease}
</style>

<script>
/* Set the saved palette before first paint so switching themes never flashes the wrong
   one on reload. Kept inline and tiny on purpose — everything else lives in the main
   script at the bottom, which also owns the <select> wiring below. */
try {
  var p = localStorage.getItem("9a-ispit-palette");
  if (p === "balanced" || p === "vivid") document.documentElement.dataset.palette = p;
} catch (e) {}
</script>

<header class="bar">
  <div class="barin">
    <div class="brand">9A<span>·</span>ISPIT</div>
    <div class="spacer"></div>
    <select id="srcSel" class="themesel" aria-label="Izvor pitanja">
      <option value="hrs">Samo HRS lista</option>
      <option value="all">HRS + priručnik</option>
    </select>
    <select id="themeSel" class="themesel" aria-label="Boje sučelja">
      <option value="muted">Prigušeno</option>
      <option value="balanced">Uravnoteženo</option>
      <option value="vivid">Živopisno</option>
    </select>
    <div id="tick" class="tick hidden">00:00</div>
    <button id="quit" class="btn hidden">Prekini</button>
  </div>
</header>

<div class="wrap">
  <section id="home">
    <div class="hero">
      <div class="eyebrow">HRS · A razred · HAREC</div>
      <h1>Priprema za radioamaterski ispit</h1>
      <p>Sva pitanja i točni odgovori iz službenih HRS ispitnih lista za A razred.
         Ispit se polaže pismeno: <strong>70&nbsp;% u svakom od tri područja</strong>.</p>
    </div>

    <div class="modes">
      <button class="mode" data-go="exam">
        <div class="spec">40 + 20 + 20 · 45/30/30 min</div>
        <h3>Simulacija ispita</h3>
        <p>Točan format i trajanje pravog ispita. Bez povratne informacije do kraja.</p>
      </button>
      <button class="mode" data-go="practice">
        <div class="spec">po područjima · bez vremena</div>
        <h3>Vježba</h3>
        <p>Odaberi područje i vježbaj s odmah vidljivim točnim odgovorom.</p>
      </button>
      <button class="mode" data-go="wrong">
        <div class="spec" id="wrongspec">0 pitanja u redu</div>
        <h3>Ponavljanje grešaka</h3>
        <p>Pitanja koja si promašio. Točan odgovor dvaput ga miče iz reda.</p>
      </button>
    </div>

    <div class="lookup">
      <label class="eyebrow" for="lookupq">Otvori pitanje po oznaci</label>
      <div class="lookuprow">
        <input id="lookupq" class="lookupin" type="text" placeholder="teh-024 · pro-011 · prv-007"
               autocomplete="off" autocapitalize="off" spellcheck="false" inputmode="text">
        <button id="lookupgo" class="btn" type="button">Otvori</button>
      </div>
      <div id="lookupmsg" class="verdict no hidden" style="margin-top:.25rem"></div>
    </div>

    <div class="sect"><h2>Gradivo</h2><div class="rule"></div></div>
    <div class="tscroll"><table id="secTable"><thead><tr>
      <th>Područje</th><th>Pitanja</th><th>Na ispitu</th><th>Vrijeme</th><th>Viđeno</th><th>Uspješnost</th>
    </tr></thead><tbody></tbody></table></div>

    <div class="sect"><h2>Po cjelinama</h2><div class="rule"></div></div>
    <div class="tscroll"><table id="subTable"><thead><tr>
      <th>Cjelina / područje</th><th>Pitanja</th><th>Viđeno</th><th>Uspješnost</th><th></th>
    </tr></thead><tbody></tbody></table></div>

    <div class="sect"><h2>Zadnji ispiti</h2><div class="rule"></div></div>
    <div id="history" class="note">Još nema odrađenih simulacija.</div>

    <p class="note" style="margin-top:2rem">
      Točni odgovori dolaze iz samih HRS ispitnih lista — u izvornim PDF-ovima označeni su crvenom bojom.
      Svako pitanje ima svoju oznaku — <span class="mono">teh-</span> za tehnički dio,
      <span class="mono">pro-</span> za propise, <span class="mono">prv-</span> za pravila i
      postupke, <span class="mono">bk-</span> za pitanja iz priručnika. Upiši je gore u „Otvori
      pitanje po oznaci”, ili više njih odvojenih zarezom. Kad je stranica otvorena izravno, a ne
      unutar okvira na claude.ai, isto radi i adresa s <span class="mono">#q=teh-024</span>.
      <button id="reset" class="btn" style="margin-left:.4rem">Obriši napredak</button>
    </p>
  </section>

  <section id="picker" class="hidden">
    <div class="eyebrow crumb"><a href="#" data-go="home">← Početna</a></div>
    <div class="sect"><h2>Vježba — odaberi područje</h2><div class="rule"></div></div>
    <div id="pickList" class="modes"></div>
    <button class="btn" data-go="home">← Natrag</button>
  </section>

  <section id="quiz" class="hidden">
    <div class="qhead">
      <span class="eyebrow crumb" id="qcrumb"></span>
      <div class="spacer"></div>
      <span class="mono" id="qcount"></span>
    </div>
    <div class="meter" style="margin-bottom:1rem"><i id="qprog" style="width:0%"></i></div>
    <div class="qcard">
      <p class="qtext" id="qtext"></p>
      <figure class="fig hidden" id="qfig"><img id="qimg" alt="Slika uz pitanje"></figure>
      <div class="opts" id="qopts"></div>
      <div class="verdict hidden" id="qverdict"></div>
      <div class="why hidden" id="qwhy"><h4 id="qwhyh">Objašnjenje</h4><div id="qwhyp"></div></div>
      <div class="cites hidden" id="qcite"></div>
      <div class="nav">
        <button class="btn" id="prev">← Prethodno</button>
        <button class="btn primary" id="next">Dalje →</button>
        <div class="spacer"></div>
        <span class="hint">tipke 1–4 · Enter</span>
      </div>
    </div>
  </section>

  <section id="result" class="hidden">
    <div class="eyebrow crumb"><a href="#" data-go="home">← Početna</a></div>
    <div class="sect"><h2 id="resTitle">Rezultat</h2><div class="rule"></div></div>
    <div id="resBody"></div>
    <div class="nav">
      <button class="btn primary" data-go="home">Početna</button>
      <button class="btn" id="reviewWrong">Pregledaj greške</button>
    </div>
  </section>
</div>

<div id="confirmMask" class="confirm-mask hidden">
  <div class="confirm-box" role="alertdialog" aria-modal="true" aria-labelledby="confirmMsg">
    <p id="confirmMsg"></p>
    <div class="nav">
      <button id="confirmYes" class="btn primary">Potvrdi</button>
      <button id="confirmNo" class="btn">Odustani</button>
    </div>
  </div>
</div>

<script>
const DATA = __PAYLOAD__;
const SEC = {
  tehnicki:{name:"Tehnički sadržaj", n:40, min:45},
  propisi :{name:"Propisi",           n:20, min:30},
  pravila :{name:"Pravila i postupci",n:20, min:30}
};
const PASS = 70, KEYS = ["a","b","c","d"];
const $ = s => document.querySelector(s);
const byId = Object.fromEntries(DATA.q.map(q => [q.id, q]));

/* ---------- persistence ---------- */
const LS = "9a-ispit-v1";
let store = {seen:{}, wrong:{}, history:[]};
try { Object.assign(store, JSON.parse(localStorage.getItem(LS) || "{}")); } catch(e){}
const save = () => { try { localStorage.setItem(LS, JSON.stringify(store)); } catch(e){} };

/* ---------- theme (colour palette) ---------- */
// Composes with, rather than replaces, the light/dark mechanism above: this only ever
// touches [data-palette], never [data-theme] — prefers-color-scheme (or a future explicit
// light/dark toggle) keeps deciding light vs dark within whichever palette is chosen here.
const LS_THEME = "9a-ispit-palette", PALETTES = ["muted","balanced","vivid"];
let palette = "muted";
try { const saved = localStorage.getItem(LS_THEME); if (PALETTES.includes(saved)) palette = saved; } catch(e){}
document.documentElement.dataset.palette = palette;
$("#themeSel").value = palette;
$("#themeSel").addEventListener("change", e => {
  palette = PALETTES.includes(e.target.value) ? e.target.value : "muted";
  document.documentElement.dataset.palette = palette;
  try { localStorage.setItem(LS_THEME, palette); } catch(e){}
});

/* ---------- question source pool: HRS exam bank only vs HRS + book ----------
   A second axis layered on top of the existing section/cjelina filters (per the item this
   implements, that filtering must not change) — poolQs() is ANDed into every section/cjelina
   filter below, on the home tables, the practice picker, and exam sampling. Lives in the
   sticky header so it's visible (and changeable) from every screen, including the practice
   picker and the home screen right before starting a simulated exam. */
const LS_SRC = "9a-ispit-src", SRC_POOLS = ["hrs","all"];
let srcPool = "hrs";
try { const saved = localStorage.getItem(LS_SRC); if (SRC_POOLS.includes(saved)) srcPool = saved; } catch(e){}
const poolQs = () => DATA.q.filter(q => srcPool === "all" || q.src === "hrs");
$("#srcSel").querySelector('option[value="hrs"]').textContent =
  "Samo HRS lista (" + DATA.q.filter(q=>q.src==="hrs").length + ")";
$("#srcSel").querySelector('option[value="all"]').textContent =
  "HRS + priručnik (" + DATA.q.length + ")";
$("#srcSel").value = srcPool;
$("#srcSel").addEventListener("change", e => {
  srcPool = SRC_POOLS.includes(e.target.value) ? e.target.value : "hrs";
  try { localStorage.setItem(LS_SRC, srcPool); } catch(e){}
  if(!$("#home").classList.contains("hidden")) home();
  if(!$("#picker").classList.contains("hidden")) buildPicker();
});

/* ---------- helpers ---------- */
const shuffle = a => { for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; };
const sample  = (arr,n) => shuffle(arr.slice()).slice(0,n);
const pct     = (a,b) => b ? Math.round(100*a/b) : 0;
const mmss    = s => String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0");

function record(q, ok){
  const s = store.seen[q.id] || {n:0,ok:0};
  s.n++; if(ok) s.ok++;
  store.seen[q.id] = s;
  if(ok){ if(store.wrong[q.id]!==undefined){ store.wrong[q.id]--; if(store.wrong[q.id]<=0) delete store.wrong[q.id]; } }
  else store.wrong[q.id] = 2;
  save();
}

/* ---------- session ---------- */
let S = null;

function start(mode, opts={}){
  let items;
  if(mode==="exam"){
    // Section sizes (SEC[k].n), timing and the 70%-per-area pass rule stay tied to the real
    // HRS exam structure regardless of pool — only which items can fill each section changes.
    items = [];
    for(const k of Object.keys(SEC)) items = items.concat(sample(poolQs().filter(q=>q.s===k), SEC[k].n));
  } else if(mode==="wrong"){
    items = shuffle(Object.keys(store.wrong).map(id=>byId[id]).filter(Boolean));
    if(!items.length){ alert("Nema pitanja u redu za ponavljanje."); return; }
  } else if(opts.items){
    items = opts.items.slice();          // deep link: exactly these, in the order given
  } else {
    items = shuffle(DATA.q.filter(opts.filter));
  }
  S = {mode, i:0, items:items.map(q=>({q, order:shuffle(KEYS.slice()), pick:null, done:false})),
       started:Date.now(), limit: mode==="exam" ? Object.values(SEC).reduce((t,s)=>t+s.min*60,0) : 0};
  show("quiz"); $("#quit").classList.toggle("hidden", mode==="single");
  if(mode==="exam"){ $("#tick").classList.remove("hidden"); timer(); }
  render();
}

let tid = null;
function timer(){
  clearInterval(tid);
  tid = setInterval(()=>{
    const left = S.limit - Math.floor((Date.now()-S.started)/1000);
    $("#tick").textContent = mmss(Math.max(left,0));
    $("#tick").classList.toggle("warn", left < 300);
    if(left<=0){ clearInterval(tid); finish(); }
  }, 250);
}

function render(){
  const it = S.items[S.i], q = it.q;
  const inExam = S.mode === "exam";
  $("#qcrumb").innerHTML = "";
  // Home link: first thing in the breadcrumb, on every quiz screen (practice, exam, wrong-
  // review, and single deep-linked questions alike) — unlike the section/cjelina links below,
  // it stays live even during an exam, going through the same leaveQuiz() confirm gate as
  // #quit so it can't be used to silently discard a running attempt.
  const homeEl = document.createElement("a");
  homeEl.href = "#"; homeEl.textContent = "← Početna"; homeEl.title = "Povratak na početnu";
  homeEl.onclick = e => { e.preventDefault(); leaveQuiz(); };
  $("#qcrumb").append(homeEl, " · ");
  // The section and cjelina names are practice entry points: clicking either starts a new
  // practice session filtered to it. During an exam they stay inert text — following either
  // would blow away the running attempt, same as the id permalink below.
  const secEl = document.createElement(inExam ? "span" : "a");
  secEl.textContent = SEC[q.s].name;
  if(!inExam){
    const secKey = q.s;
    secEl.href = "#"; secEl.title = "Vježbaj ovo područje";
    secEl.onclick = e => { e.preventDefault(); start("practice", {filter: qq => qq.s === secKey}); };
  }
  $("#qcrumb").append(secEl);
  if(q.sub){
    $("#qcrumb").append(" · ");
    const subEl = document.createElement(inExam ? "span" : "a");
    subEl.textContent = q.sub.replace(/^\d+\.\s*/,"");
    if(!inExam){
      const subKey = q.sub;
      subEl.href = "#"; subEl.title = "Vježbaj ovu cjelinu";
      subEl.onclick = e => { e.preventDefault(); start("practice", {filter: qq => qq.sub === subKey}); };
    }
    $("#qcrumb").append(subEl);
  }
  $("#qcrumb").append(" ");
  const tg = document.createElement("span"); tg.className = "tag";
  tg.textContent = q.src === "hrs" ? "HRS lista" : "priručnik";
  $("#qcrumb").append(tg, " ");
  // The id is the permalink. During an exam it is inert text — following it would blow away
  // the running attempt.
  const idt = document.createElement(inExam ? "span" : "a");
  idt.className = "tag"; idt.textContent = q.id;
  if(!inExam){ idt.href = "#q=" + q.id; idt.title = "Poveznica na ovo pitanje"; }
  $("#qcrumb").append(idt);
  if(!inExam) setUrlQ(q.id);
  $("#qcount").textContent = (S.i+1) + " / " + S.items.length;
  $("#qprog").style.width = pct(S.i, S.items.length) + "%";
  $("#qtext").textContent = q.q;

  const fig = $("#qfig");
  // q.f is "images/<id>.png", relative to this page — works unchanged under file:// and
  // http(s)://, unlike fetch()/XHR which file:// blocks with a CORS error.
  if(q.f){ $("#qimg").src = q.f; fig.classList.remove("hidden"); } else fig.classList.add("hidden");

  const wrapEl = $("#qopts"); wrapEl.innerHTML = "";
  it.order.forEach((k, idx) => {
    const b = document.createElement("button");
    b.className = "opt"; b.type = "button";
    b.innerHTML = '<span class="k">'+(idx+1)+'.</span><span></span>';
    b.lastChild.textContent = q.o[k] || "";
    if(it.pick === k) b.classList.add("sel");
    if(it.done){
      b.disabled = true;
      if(k === q.a) b.classList.add("ok");
      else if(k === it.pick) b.classList.add("no");
    }
    b.onclick = () => pick(k);
    wrapEl.appendChild(b);
  });

  const v = $("#qverdict");
  if(it.done && S.mode !== "exam"){
    const ok = it.pick === q.a;
    v.className = "verdict " + (ok ? "ok" : "no");
    v.textContent = ok ? "Točno." : "Netočno — točan odgovor je označen zeleno.";
    v.classList.remove("hidden");
  } else v.classList.add("hidden");

  const why = $("#qwhy");
  if(it.done && S.mode !== "exam" && q.e){
    why.className = "why" + (q.flag === "conflict" ? " warn" : q.flag === "check" ? " check" : "");
    $("#qwhyh").textContent = q.flag === "conflict" ? "Propis kaže drugačije"
                            : q.flag === "check"    ? "Provjeriti s klubom" : "Objašnjenje";
    // Built as DOM nodes rather than innerHTML: the note text is ours, but it carries
    // maths and quoted regulation, and textContent keeps any stray < or & literal.
    const body = $("#qwhyp");
    body.textContent = "";
    (q.e || "").split(/\n\n+/).forEach(para => {
      const p = document.createElement("p");
      p.className = "wp";
      p.textContent = para.replace(/\n/g, " ");
      body.appendChild(p);
    });
    (q.fx || []).forEach(line => {
      const f = document.createElement("pre");
      f.className = "fx";
      f.textContent = line;
      body.appendChild(f);
    });
    if((q.lk || []).length){
      const nav = document.createElement("div");
      nav.className = "lk";
      nav.appendChild(document.createTextNode("Dalje: "));
      q.lk.forEach((l, i) => {
        if(i) nav.appendChild(document.createTextNode(" · "));
        const a = document.createElement("a");
        a.href = l.url; a.target = "_blank"; a.rel = "noopener noreferrer";
        a.textContent = l.label;
        nav.appendChild(a);
      });
      body.appendChild(nav);
    }
    why.classList.remove("hidden");
  } else why.classList.add("hidden");

  const cite = $("#qcite");
  if(it.done){
    const rows = [];
    if(q.cs) rows.push(["Pitanje", q.cs]);
    (q.c || []).forEach(c => rows.push(["Izvor", c]));
    cite.innerHTML = rows.map(([lab, c]) => {
      const meta = DATA.src[c.src] || {};
      return '<div>' + lab + ': <b>' + c.src + '</b> — ' + c.loc +
             (meta.file ? ' <span style="opacity:.7">(' + meta.file + ')</span>' : '') + '</div>';
    }).join("");
    cite.classList.toggle("hidden", !rows.length);
  } else cite.classList.add("hidden");

  $("#prev").disabled = S.i === 0;
  $("#next").textContent = S.i < S.items.length-1 ? "Dalje →"
                         : S.mode === "single" ? "Početna ▸" : "Završi ▸";
}

function pick(k){
  const it = S.items[S.i];
  if(it.done) return;
  it.pick = k;
  if(S.mode === "exam"){ render(); return; }   // exam: no feedback until the end
  it.done = true;
  record(it.q, k === it.q.a);
  render();
}

function step(d){
  if(S.i + d < 0) return;
  if(S.i + d >= S.items.length){ finish(); return; }
  S.i += d; render();
}

function finish(){
  clearInterval(tid);
  $("#tick").classList.add("hidden"); $("#quit").classList.add("hidden");
  if(S.mode === "single"){ show("home"); return; }   // a linked question has no score screen
  if(S.mode === "exam") S.items.forEach(it => { if(!it.done){ it.done = true; record(it.q, it.pick === it.q.a); } });

  const per = {};
  for(const it of S.items){
    const s = per[it.q.s] || (per[it.q.s] = {n:0, ok:0});
    s.n++; if(it.pick === it.q.a) s.ok++;
  }
  const tot = Object.values(per).reduce((t,s)=>({n:t.n+s.n, ok:t.ok+s.ok}), {n:0,ok:0});
  const passed = S.mode === "exam" && Object.entries(per).every(([k,s]) => pct(s.ok,s.n) >= PASS);

  let h = "";
  if(S.mode === "exam"){
    h += '<div class="stat" style="margin-bottom:1rem"><div class="eyebrow">Ishod</div>' +
         '<div class="big" style="color:var(--'+(passed?"good":"bad")+')">'+(passed?"POLOŽENO":"PALO")+'</div>' +
         '<div class="note">Za prolaz treba ' + PASS + ' % u svakom području zasebno.</div></div>';
  }
  h += '<div class="grid3">';
  for(const [k,s] of Object.entries(per)){
    const p = pct(s.ok, s.n), ok = p >= PASS;
    h += '<div class="stat"><div class="eyebrow">'+SEC[k].name+'</div>' +
         '<div class="big">'+p+'&thinsp;%</div>' +
         '<div class="mono" style="font-size:.8rem;color:var(--muted)">'+s.ok+' / '+s.n+
         ' <span class="pill '+(ok?"ok":"no")+'">'+(ok?"prolaz":"pad")+'</span></div>' +
         '<div class="meter" style="margin-top:.55rem"><i class="'+(ok?"ok":"no")+'" style="width:'+p+'%"></i>' +
         '<span class="thr" style="left:'+PASS+'%"></span></div></div>';
  }
  h += '</div><p class="note" style="margin-top:1rem">Ukupno '+tot.ok+' / '+tot.n+
       ' ('+pct(tot.ok,tot.n)+' %). Okomita crta na traci je granica od '+PASS+' %.</p>';

  $("#resTitle").textContent = S.mode === "exam" ? "Rezultat simulacije ispita" : "Rezultat vježbe";
  $("#resBody").innerHTML = h;
  if(S.mode === "exam"){
    store.history.unshift({t:Date.now(), per, passed});
    store.history = store.history.slice(0,10); save();
  }
  show("result");
}

/* ---------- shared cjelina/area breakdown (used by both home()'s subTable and the
   practice picker, so the two never diverge) ----------
   Tehnički is the only section whose questions carry a subsection (q.sub) — the HRS source
   gives propisi and pravila no chapter headings to draw one from (book_subsections.json),
   so for those two this correctly degrades to a single whole-area group rather than
   inventing cjelina names. */
function sectionGroups(k){
  const qs = poolQs().filter(q=>q.s===k);
  const bySub = {};
  qs.forEach(q=>{ if(q.sub) (bySub[q.sub] = bySub[q.sub]||[]).push(q); });
  const groups = Object.keys(bySub).length
    ? Object.entries(bySub).sort((a,b)=>parseInt(a[0])-parseInt(b[0])).map(([name,gqs])=>({name, sub:name, qs:gqs}))
    : [{name: SEC[k].name, sub:null, qs}];
  return groups.map(g => {
    let seen=0, ok=0, tries=0;
    g.qs.forEach(q=>{ const s=store.seen[q.id]; if(s){ seen++; ok+=s.ok; tries+=s.n; } });
    return {name:g.name, sub:g.sub, qs:g.qs, seen, ok, tries};
  });
}

/* ---------- home ---------- */
function home(){
  const tb = $("#secTable").querySelector("tbody"); tb.innerHTML = "";
  for(const [k,meta] of Object.entries(SEC)){
    const qs = poolQs().filter(q=>q.s===k);
    let seen=0, ok=0, tries=0;
    qs.forEach(q=>{ const s=store.seen[q.id]; if(s){ seen++; ok+=s.ok; tries+=s.n; } });
    const tr = document.createElement("tr");
    tr.innerHTML = '<td>'+meta.name+'</td><td class="num">'+qs.length+'</td><td class="num">'+meta.n+
      '</td><td class="num">'+meta.min+' min</td><td class="num">'+seen+'</td>'+
      '<td class="num">'+(tries?pct(ok,tries)+' %':'—')+'</td>';
    tb.appendChild(tr);
  }

  const sb = $("#subTable").querySelector("tbody"); sb.innerHTML = "";
  for(const k of Object.keys(SEC)){
    sectionGroups(k).forEach(g => {
      const tr = document.createElement("tr");
      tr.innerHTML = '<td>'+g.name+'</td><td class="num">'+g.qs.length+'</td><td class="num">'+g.seen+
        '</td><td class="num">'+(g.tries?pct(g.ok,g.tries)+' %':'—')+'</td>'+
        '<td style="text-align:right"><button class="btn" data-sub="'+(g.sub||"").replace(/"/g,'&quot;')+
        '" data-sec="'+k+'">Vježbaj</button></td>';
      sb.appendChild(tr);
    });
  }
  sb.querySelectorAll("[data-sub]").forEach(b => b.onclick = () => {
    const sub = b.dataset.sub, sec = b.dataset.sec;
    const inPool = q => srcPool === "all" || q.src === "hrs";
    start("practice", {filter: sub ? (q => q.sub === sub && inPool(q)) : (q => q.s === sec && inPool(q))});
  });

  const n = Object.keys(store.wrong).length;
  $("#wrongspec").textContent = n ? n + " pitanja u redu" : "red je prazan";

  const hist = $("#history");
  if(!store.history.length) hist.innerHTML = '<p class="note">Još nema odrađenih simulacija.</p>';
  else hist.innerHTML = '<div class="tscroll"><table><thead><tr><th>Datum</th>' +
      Object.values(SEC).map(s=>'<th>'+s.name+'</th>').join("") + '<th>Ishod</th></tr></thead><tbody>' +
      store.history.map(h => '<tr><td class="mono">' + new Date(h.t).toLocaleDateString("hr-HR") + '</td>' +
        Object.keys(SEC).map(k => { const s = h.per[k]; const p = s ? pct(s.ok,s.n) : 0;
          return '<td class="num" style="color:var(--'+(p>=PASS?"good":"bad")+')">'+p+' %</td>'; }).join("") +
        '<td><span class="pill '+(h.passed?"ok":"no")+'">'+(h.passed?"položeno":"palo")+'</span></td></tr>').join("") +
      '</tbody></table></div>';
}

function buildPicker(){
  const el = $("#pickList"); el.innerHTML = "";
  const add = (title, desc, spec, filter) => {
    const b = document.createElement("button");
    b.className = "mode";
    b.innerHTML = '<div class="spec"></div><h3></h3><p></p>';
    b.children[0].textContent = spec; b.children[1].textContent = title; b.children[2].textContent = desc;
    b.onclick = () => start("practice", {filter});
    el.appendChild(b);
  };
  const inPool = q => srcPool === "all" || q.src === "hrs";
  for(const [k,meta] of Object.entries(SEC)){
    const n = poolQs().filter(q=>q.s===k).length;
    add(meta.name, "Sva pitanja iz ovog područja, nasumičnim redom.", n+" pitanja", q=>q.s===k && inPool(q));
    // Cjelina rows exist only where the data has them (tehnicki) — see sectionGroups() above.
    // Propisi/pravila stay a single whole-area entry, already added as the button just above.
    const groups = sectionGroups(k);
    if(groups.length > 1 || groups[0].sub){
      groups.forEach(g => {
        const stat = g.tries ? pct(g.ok,g.tries)+"% uspješnost" : "još bez pokušaja";
        add(g.name.replace(/^\d+\.\s*/,""),
            "Cjelina unutar „" + meta.name + "”. Viđeno " + g.seen + " · " + stat + ".",
            g.qs.length+" pitanja", q=>q.sub===g.sub && inPool(q));
      });
    }
  }
  const nh = DATA.q.filter(q=>q.src==="hrs").length, nb = DATA.q.filter(q=>q.src==="book").length;
  add("Sve iz HRS lista", "Sva pitanja iz sve tri službene liste.", nh+" pitanja", q=>q.src==="hrs");
  add("Dodatna iz priručnika", "Pitanja iz priručnika Radiokomunikacije, s odgovorima iz tablice u knjizi. Ne ulaze u simulaciju ispita.", nb+" pitanja", q=>q.src==="book");
}

/* ---------- confirm ----------
   window.confirm() (and alert/prompt) is silently a no-op inside a sandboxed iframe that
   lacks allow-modals — the call returns undefined without showing anything, so
   `if(confirm(...))` is always false. That's exactly how this page runs embedded on
   claude.ai, so start-exam / quit / reset all need their own confirmation UI instead. */
let confirmPrev = null;
function askConfirm(msg, onYes){
  $("#confirmMsg").textContent = msg;
  $("#confirmMask").classList.remove("hidden");
  confirmPrev = document.activeElement;
  $("#confirmYes").focus();
  const onKey = e => { if(e.key === "Escape"){ e.preventDefault(); done(false); } };
  function done(ok){
    $("#confirmMask").classList.add("hidden");
    document.removeEventListener("keydown", onKey, true);
    if(confirmPrev && confirmPrev.focus) confirmPrev.focus();
    if(ok) onYes();
  }
  document.addEventListener("keydown", onKey, true);
  $("#confirmYes").onclick = () => done(true);
  $("#confirmNo").onclick = () => done(false);
  $("#confirmMask").onclick = e => { if(e.target === $("#confirmMask")) done(false); };
}

// Shared by #quit and the breadcrumb home link on the quiz screen, so both exit paths give the
// identical confirm-before-losing-progress prompt (see P1-0038 — a silent window.confirm()
// no-op here made both start-exam and quit look dead in a sandboxed iframe). A "single"-mode
// session (deep-linked question) has nothing to lose, so it skips the prompt, same as #quit
// already being hidden for that mode.
function leaveQuiz(){
  if(S && S.mode !== "single") askConfirm("Prekinuti i odbaciti ovaj pokušaj?", () => show("home"));
  else show("home");
}

/* ---------- routing ---------- */
function show(id){
  ["home","picker","quiz","result"].forEach(s => $("#"+s).classList.toggle("hidden", s !== id));
  if(id!=="quiz") setUrlQ("");
  if(id!=="home") $("#lookupmsg").classList.add("hidden");
  if(id==="home"){ clearInterval(tid); $("#tick").classList.add("hidden"); $("#quit").classList.add("hidden"); home(); }
  window.scrollTo({top:0, behavior:"instant"});
}

/* ---------- deep links: quiz.html#q=teh-024 (also #teh-024, or a comma-separated list) ---------- */
function qidFromUrl(){
  const m = (location.hash + "&" + location.search).match(/[#?&]q=([^&]+)/i);
  if(m) return decodeURIComponent(m[1]).trim().toLowerCase();
  const one = "(?:bk-)?[a-z]{3}-[a-z0-9-]+";
  const bare = location.hash.match(new RegExp("^#(" + one + "(?:,\\s*" + one + ")*)$", "i"));
  return bare ? bare[1].toLowerCase() : "";
}

function setUrlQ(id){
  const want = id ? "#q=" + id : "";
  if((location.hash || "") === want) return;
  // replaceState throws on file:// in some browsers (origin "null"); assigning the hash always
  // works, it just leaves a history entry behind.
  try { history.replaceState(null, "", want || location.pathname + location.search); }
  catch(e){ location.hash = want; }
}

// Accepts what people actually paste: "teh-024", "TEH 24", "#q=teh-024", a whole URL tail.
// Ids come in two shapes — HRS "teh-024" / "pro-011" / "prv-007" (three digits, and a few like
// "teh-186b"), and priručnik "bk-teh-1-01" (two). So an unpadded number is tried at both widths,
// with and without the separator, and only then given up on.
function normId(raw){
  const s = String(raw).trim().toLowerCase()
              .replace(/^.*?[#?&]q=/, "").replace(/^#/, "").replace(/[\s_]+/g, "");
  if(byId[s]) return s;
  const m = s.match(/^(.*?)-?(\d+)$/);
  if(m) for(const stem of [m[1] + "-", m[1]])
    for(const w of [3, 2]){
      const p = stem + m[2].padStart(w, "0");
      if(byId[p]) return p;
    }
  return s;
}

function openById(raw){
  const items = raw.split(",").map(s => byId[normId(s)]).filter(Boolean);
  if(!items.length){
    const msg = $("#lookupmsg");
    msg.textContent = "Nema pitanja s oznakom „" + raw + "”.";
    show("home"); msg.classList.remove("hidden");
    setUrlQ("");
    return false;
  }
  start("single", {items});
  return true;
}

window.addEventListener("hashchange", () => {
  if(S && S.mode === "exam") return;                       // never derail a running simulation
  const id = qidFromUrl();
  if(!id){ if(!$("#quiz").classList.contains("hidden")) show("home"); return; }
  const cur = S && S.items[S.i];
  if(cur && cur.q.id === id && !$("#quiz").classList.contains("hidden")) return;   // our own update
  openById(id);
});

document.addEventListener("click", e => {
  const go = e.target.closest("[data-go]");
  if(!go) return;
  const d = go.dataset.go;
  if(d==="practice"){ buildPicker(); show("picker"); }
  else if(d==="exam"){
    const poolLabel = srcPool === "all" ? "HRS + priručnik" : "samo HRS lista";
    askConfirm("Simulacija ispita: 80 pitanja, 105 minuta ukupno · izvor: " + poolLabel + ". Počinjemo?", () => start("exam"));
  }
  else if(d==="wrong") start("wrong");
  else show(d);
});
$("#next").onclick = () => step(1);
$("#prev").onclick = () => step(-1);
$("#quit").onclick = leaveQuiz;
$("#reset").onclick = () => askConfirm("Obrisati sav napredak?", () => { store={seen:{},wrong:{},history:[]}; save(); home(); });
$("#reviewWrong").onclick = () => start("wrong");

// No <form>: a sandboxed frame may not have allow-forms, and a blocked submit fails silently.
const doLookup = () => { const v = $("#lookupq").value.trim(); if(v) openById(v); };
$("#lookupgo").onclick = doLookup;
// stopPropagation matters: without it this same Enter keeps bubbling to the document handler
// below, which by then sees the freshly opened question and reads it as "next" — closing it.
$("#lookupq").addEventListener("keydown", e => {
  if(e.key !== "Enter") return;
  e.preventDefault(); e.stopPropagation();
  doLookup();
});

document.addEventListener("keydown", e => {
  // Never steal keys from a field someone is typing in — 1–4 and Enter are quiz controls only.
  const t = e.target;
  if(t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
  if($("#quiz").classList.contains("hidden")) return;
  if(e.key >= "1" && e.key <= "4"){ const it = S.items[S.i]; const k = it.order[+e.key - 1]; if(k) pick(k); }
  else if(e.key === "Enter" || e.key === "ArrowRight") step(1);
  else if(e.key === "ArrowLeft") step(-1);
});

const boot = qidFromUrl();
if(!boot || !openById(boot)) show("home");
</script>
"""

out = DST / "quiz.html"
out.write_text(HTML.replace("__PAYLOAD__", payload), encoding="utf-8")
print(f"wrote {out}  ({out.stat().st_size//1024} KB)  questions={len(live)}")
