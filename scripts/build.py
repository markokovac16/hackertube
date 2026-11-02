#!/usr/bin/env python3
import json, sys
from rule import qualifies, rising
AGG, CACHE, OUT, MIN_REC, MIN_YEARS = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
EXCLUDE = {"dQw4w9WgXcQ"}
rows, cache = json.load(open(AGG)), json.load(open(CACHE))
out = []
for r in rows:
    if r["id"] in EXCLUDE: continue
    if not qualifies(r, MIN_REC, MIN_YEARS): continue
    m = cache.get(r["id"])
    if not m or not m["ok"] or not m.get("title"): continue
    if m["status"] == "UNPLAYABLE" and ("members" in m["reason"] or "live stream" in m["reason"]): continue
    out.append({
        "id": r["id"], "title": m["title"], "channel": m["channel"], "channelId": m.get("channelId"),
        "seconds": m["seconds"], "views": m["views"], "category": m.get("category") or "Other",
        "published": m.get("published"), "embeddable": m.get("embeddable", True) and m["status"] == "OK",
        "description": m.get("description", ""),
        "rec": r["recommenders"], "threads": r["threads"], "mentions": r["mentions"],
        "years": r["years"], "rising": rising(r, MIN_REC, MIN_YEARS), "first": r["first"], "last": r["last"],
        "subs": sorted(r["submissions"], key=lambda s: -s["points"])[:10],
        "comments": [[c["id"], c["author"], c["t"]] for c in r["comments"]],
    })
json.dump({"generated": __import__("time").strftime("%Y-%m-%d"), "minRec": MIN_REC,
           "minYears": MIN_YEARS, "videos": out}, open(OUT, "w"), separators=(",", ":"))
print("site videos:", len(out), file=sys.stderr)
