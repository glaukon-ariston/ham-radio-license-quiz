"""Print the next item to work on, without anyone having to read the queue.

    python queue/pick.py          # the next item, its cluster, its siblings
    python queue/pick.py --list   # the whole queue, one line each

This script reads every item body; that is cheap because only its five lines of output
reach an agent's context. Nothing else should open `queue/todo/` in bulk.

An item is READY when `blocked-by:` is empty. It is BLOCKED when that field names an item
number still sitting in todo/, or names anything else at all (a person, a ruling) — those
clear when a human clears them. An item still carrying template placeholders is a DRAFT and
is never picked.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
TODO = HERE / "todo"
NAME = re.compile(r"^P(\d)-(\d{4})-")
EMPTY = {"", "-", "—", "none", "n/a"}


def field(text, key):
    m = re.search(rf"^{key}:[ \t]*(.*)$", text, re.M)
    return m.group(1).strip() if m else ""


def load():
    items = []
    for p in sorted(TODO.glob("*.md")):
        m = NAME.match(p.name)
        if not m:
            continue
        text = p.read_text(encoding="utf-8")
        blocked_by = field(text, "blocked-by")
        cluster = field(text, "cluster")
        draft = "<" in cluster or "<" in blocked_by or "<" in field(text, "files")
        items.append({
            "path": p, "band": int(m.group(1)), "num": m.group(2),
            "cluster": cluster, "blocked_by": blocked_by, "draft": draft,
        })
    live = {i["num"] for i in items}
    for i in items:
        dep = i["blocked_by"]
        if i["draft"]:
            i["state"] = "draft"
        elif dep.lower() in EMPTY:
            i["state"] = "ready"
        elif any(n in live for n in re.findall(r"\d{4}", dep)):
            i["state"] = "blocked"
        elif re.fullmatch(r"[\d\s,]+", dep):
            i["state"] = "ready"          # every numbered dependency has landed
        else:
            i["state"] = "blocked"        # a person, a ruling — human clears it
    return items


def main():
    items = load()
    if not items:
        print("queue: empty")
        return

    if "--list" in sys.argv:
        for i in sorted(items, key=lambda i: (i["band"], i["num"])):
            mark = {"ready": " ", "blocked": "x", "draft": "?"}[i["state"]]
            dep = f"  <- {i['blocked_by']}" if i["state"] == "blocked" else ""
            print(f" {mark} P{i['band']}-{i['num']}  {i['cluster']:24s} {i['path'].stem[8:]}{dep}")

    ready = sorted((i for i in items if i["state"] == "ready"),
                   key=lambda i: (i["band"], i["num"]))
    counts = {s: sum(1 for i in items if i["state"] == s) for s in ("ready", "blocked", "draft")}
    tally = (f"queue:    {len(items)} items — {counts['ready']} ready, "
             f"{counts['blocked']} blocked, {counts['draft']} draft")

    if not ready:
        print("item:     none ready")
        print(tally)
        return

    pick = ready[0]
    siblings = [i for i in ready[1:]
                if i["cluster"] == pick["cluster"] and i["band"] == pick["band"]]
    print(f"item:     {pick['path'].relative_to(HERE.parent).as_posix()}")
    print(f"cluster:  {pick['cluster']}")
    print(f"siblings: {' '.join(f'P{i['band']}-{i['num']}' for i in siblings) or 'none'}")
    print(tally)


if __name__ == "__main__":
    main()
