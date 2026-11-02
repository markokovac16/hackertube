#!/usr/bin/env python3
import json, re, sys, html
from collections import defaultdict
from datetime import datetime, timezone

RAW, OUT = sys.argv[1], sys.argv[2]
ID = r"([A-Za-z0-9_-]{11})(?![A-Za-z0-9_-])"
PATTERNS = [
    re.compile(r"(?:https?://)?(?:[\w-]+\.)?youtube(?:-nocookie)?\.com/(?:watch/?\?(?:[^\s\"'<>#]*?&(?:amp;)?)?v=|embed/|v/|shorts/|live/|e/)" + ID, re.I),
    re.compile(r"(?:https?://)?youtu\.be/" + ID, re.I),
    re.compile(r"youtube\.com/(?:watch/|[^\s\"'<>]*#!v=|[^\s\"'<>]*#p/(?:u|a|c|f|search)/\d+/)" + ID, re.I),
]

def ids_in(text):
    if not text: return set()
    t = html.unescape(html.unescape(text))
    t = t.replace("%3D", "=").replace("%3F", "?").replace("%26", "&")
    out = set()
    for p in PATTERNS:
        out.update(m.group(1) for m in p.finditer(t))
    return out

vids = defaultdict(lambda: {"items": []})
for line in open(RAW):
    h = json.loads(line)
    is_story = h.get("comment_text") is None
    text = (h.get("url") or "") if is_story else h["comment_text"]
    for vid in ids_in(text):
        vids[vid]["items"].append({
            "id": int(h["objectID"]), "author": h.get("author"),
            "story": int(h["objectID"]) if is_story else h.get("story_id"),
            "t": h["created_at_i"], "kind": "story" if is_story else "comment",
            "points": h.get("points") or 0, "title": h.get("title"),
        })

rows = []
for vid, v in vids.items():
    items = [i for i in v["items"] if i["author"]]
    authors = {i["author"] for i in items}
    threads = {i["story"] for i in items if i["story"]}
    years = {datetime.fromtimestamp(i["t"], timezone.utc).year for i in items}
    rows.append({
        "id": vid, "recommenders": len(authors), "threads": len(threads),
        "mentions": len(items), "years": sorted(years),
        "first": min(i["t"] for i in items) if items else 0,
        "last": max(i["t"] for i in items) if items else 0,
        "submissions": [{"id": i["id"], "title": i["title"], "points": i["points"], "t": i["t"]}
                        for i in items if i["kind"] == "story"],
        "comments": sorted([{"id": i["id"], "author": i["author"], "t": i["t"]}
                            for i in items if i["kind"] == "comment"], key=lambda c: c["t"]),
    })
rows.sort(key=lambda r: (-r["recommenders"], -len(r["years"])))
json.dump(rows, open(OUT, "w"))
print("videos:", len(rows), file=sys.stderr)
for k in (2, 3, 5, 8, 10, 15, 20):
    print(f"recommenders>={k} & years>=2:", sum(1 for r in rows if r["recommenders"] >= k and len(r["years"]) >= 2), file=sys.stderr)
