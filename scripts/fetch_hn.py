#!/usr/bin/env python3
import json, sys, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

API = "https://hn.algolia.com/api/v1/search_by_date"
OUT = sys.argv[1]
START, END = 1160000000, int(time.time()) + 86400

def get(params, tries=6):
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(2 ** i)
    raise RuntimeError(url)

def base(query, tags, lo, hi, n):
    return {"query": query, "tags": tags, "hitsPerPage": n,
            "numericFilters": f"created_at_i>={lo},created_at_i<{hi}",
            "attributesToRetrieve": "comment_text,author,story_id,created_at_i,url,title,points,objectID",
            "attributesToHighlight": "", "typoTolerance": "false"}

def ranges(query, tags, lo, hi):
    n = get(base(query, tags, lo, hi, 0))["nbHits"]
    if n == 0: return []
    if n < 1000 or hi - lo <= 60: return [(lo, hi)]
    mid = (lo + hi) // 2
    return ranges(query, tags, lo, mid) + ranges(query, tags, mid, hi)

def fetch(job):
    query, tags, lo, hi = job
    return get(base(query, tags, lo, hi, 1000))["hits"]

jobs = []
for query, tags in [("youtube", "comment"), ("youtu.be", "comment"),
                    ("youtube", "story"), ("youtu.be", "story")]:
    years = [(y, min(y + 31557600, END)) for y in range(START, END, 31557600)]
    with ThreadPoolExecutor(8) as ex:
        for rs in ex.map(lambda r: ranges(query, tags, *r), years):
            jobs += [(query, tags, a, b) for a, b in rs]
    print(query, tags, "ranges so far", len(jobs), file=sys.stderr)

seen = {}
with ThreadPoolExecutor(8) as ex:
    for i, hits in enumerate(ex.map(fetch, jobs)):
        for h in hits:
            seen[h["objectID"]] = h
        if i % 50 == 0: print(f"{i}/{len(jobs)} items={len(seen)}", file=sys.stderr)
with open(OUT, "w") as f:
    for h in seen.values(): f.write(json.dumps(h) + "\n")
print("done", len(seen), file=sys.stderr)
