"""Fetch every external link in the expanded notes and report the ones that are not there.

The agents are told to confirm each link themselves; this is the backstop that catches a
redirect to a search page or a Croatian Wikipedia article that never existed. Wikipedia
answers 404 for a missing article, but it also serves a "no article" stub for some
redirects, so the title is checked too.
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
UA = {"User-Agent": "ham-quiz-linkcheck/1.0 (personal study material)"}

seen = defaultdict(list)     # url -> [qid, ...]
for f in sorted(HERE.glob("notes_zzz_expanded_*.json")):
    for qid, spec in json.load(open(f, encoding="utf-8")).items():
        if qid.startswith("_"):
            continue
        for l in spec.get("links", []):
            seen[l["url"]].append(f"{f.stem.replace('notes_zzz_expanded_', '')}/{qid}")

def disambiguations(urls):
    """Wikipedia titles that are disambiguation pages rather than articles.

    These answer 200, so fetching alone never catches them -- hr.wikipedia's `Filtar`,
    `Kondenzator`, `Oscilator` and `Zavojnica` all shipped as links before this check
    existed. The API's pageprops says so definitively; scraping the HTML for the word
    "disambiguation" does not, because it appears in ordinary page chrome too.
    """
    import collections
    bad, by_lang = set(), collections.defaultdict(list)
    for u in urls:
        if ".wikipedia.org/wiki/" not in u:
            continue
        lang = u.split("//", 1)[1].split(".", 1)[0]
        by_lang[lang].append(urllib.parse.unquote(u.rsplit("/wiki/", 1)[1]).replace("_", " "))
    for lang, titles in by_lang.items():
        for i in range(0, len(titles), 40):
            chunk = titles[i:i + 40]
            api = (f"https://{lang}.wikipedia.org/w/api.php?action=query&prop=pageprops"
                   f"&redirects=1&format=json&titles=" + urllib.parse.quote("|".join(chunk)))
            try:
                with urllib.request.urlopen(urllib.request.Request(api, headers=UA),
                                            timeout=25) as r:
                    pages = json.loads(r.read().decode())["query"]["pages"]
            except Exception as e:
                print(f"  ?    could not query {lang}.wikipedia pageprops: {e}")
                continue
            for p in pages.values():
                if "disambiguation" in (p.get("pageprops") or {}):
                    bad.add((lang, p["title"]))
    return bad


print(f"{len(seen)} distinct urls\n")
disambig = disambiguations(seen)
for lang, title in sorted(disambig):
    print(f"  BAD  disambiguation page  {lang}.wikipedia: {title}")
    print("       links there teach nothing — point at the real article")
bad = len(disambig)
for url in sorted(seen):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            code, final = r.status, r.geturl()
            body = r.read(4000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        code, final, body = e.code, url, ""
    except Exception as e:                                   # DNS, TLS, timeout
        code, final, body = f"ERR {type(e).__name__}", url, ""
    ok = code == 200
    # a Wikipedia article that does not exist still renders, with this in the body
    if ok and "wikipedia.org/wiki/" in url and "Wikipedia does not have an article" in body:
        ok, code = False, "200 but no such article"
    if ok and "wikipedia.org/wiki/" in url:
        want = urllib.parse.unquote(url.rsplit("/wiki/", 1)[1]).replace("_", " ").lower()
        if want and want.split("#")[0] not in body.lower():
            print(f"  ?    {code}  {url}\n       title not found in the page head — check by eye")
    if not ok:
        bad += 1
        print(f"  BAD  {code}  {url}\n       used by {', '.join(seen[url][:6])}")
    if ok and final.rstrip("/") != url.rstrip("/"):
        print(f"  ->   redirected  {url}\n       to {final}")

print(f"\n{bad} bad of {len(seen)}")
sys.exit(1 if bad else 0)
