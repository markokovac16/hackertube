#!/usr/bin/env python3
import json, sys, time, urllib.request, os, re
from concurrent.futures import ThreadPoolExecutor
from rule import qualifies

AGG, CACHE, MIN_REC, MIN_YEARS = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
HDRS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9", "Cookie": "CONSENT=YES+1; SOCS=CAI"}
dec = json.JSONDecoder()

def fetch(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def oembed(vid):
    try:
        return json.loads(fetch(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"))
    except Exception:
        return None

def meta(vid):
    for attempt in range(4):
        try:
            page = fetch(f"https://www.youtube.com/watch?v={vid}&hl=en&gl=US")
            i = page.find("ytInitialPlayerResponse = ")
            if i < 0: raise ValueError("no player response")
            pr, _ = dec.raw_decode(page, i + len("ytInitialPlayerResponse = "))
            ps = pr.get("playabilityStatus", {})
            status, reason = ps.get("status"), ps.get("reason", "")
            if "not a bot" in reason: raise ValueError("bot check")
            vd = pr.get("videoDetails")
            if status in ("ERROR", "UNPLAYABLE") or not vd:
                if oembed(vid) is None:
                    return {"ok": False, "status": status, "reason": reason}
            mf = pr.get("microformat", {}).get("playerMicroformatRenderer", {})
            oe = None if vd else oembed(vid)
            return {"ok": True, "status": status, "reason": reason,
                    "title": (vd or {}).get("title") or (oe or {}).get("title"),
                    "channel": (vd or {}).get("author") or (oe or {}).get("author_name"),
                    "channelId": (vd or {}).get("channelId"),
                    "seconds": int((vd or {}).get("lengthSeconds") or 0),
                    "views": int((vd or {}).get("viewCount") or 0),
                    "category": mf.get("category"),
                    "published": (mf.get("publishDate") or mf.get("uploadDate") or "")[:10],
                    "embeddable": ps.get("playableInEmbed", True),
                    "description": ((vd or {}).get("shortDescription") or "")[:600]}
        except Exception as e:
            time.sleep((60 if '429' in str(e) else 3) * (attempt + 1))
    return None

rows = json.load(open(AGG))
cands = [r["id"] for r in rows if qualifies(r, MIN_REC, MIN_YEARS)]
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
todo = [v for v in cands if v not in cache]
print(f"candidates={len(cands)} todo={len(todo)}", file=sys.stderr)
with ThreadPoolExecutor(int(os.environ.get('META_WORKERS', 6))) as ex:
    for n, (vid, m) in enumerate(zip(todo, ex.map(meta, todo))):
        if m is not None: cache[vid] = m
        if n % 100 == 0:
            print(n, file=sys.stderr); json.dump(cache, open(CACHE, "w"))
json.dump(cache, open(CACHE, "w"))
print("failed transiently:", sum(1 for v in cands if v not in cache),
      "gone:", sum(1 for v in cands if v in cache and not cache[v]["ok"]), file=sys.stderr)
