# HackerTube

A YouTube-style site that only lists videos Hacker News users have recommended again and again over the years.

## Inclusion rule
A video gets in only if **at least 8 distinct HN accounts** linked it (in comments or story submissions), in **at least 3 distinct calendar years**.
Repeat links from the same user count once.

Newer videos can't have 3 years of history yet, so a video first linked in the last 3 years also qualifies as **Rising**
if 5+ distinct accounts linked it in 5+ separate threads, with mentions spread over at least 60 days. See `scripts/rule.py`.

Deleted, private and members-only videos are dropped, and so is the Rickroll.

## Rebuild the data
```sh
./update.sh          # fetch HN → aggregate → YouTube metadata → site/videos.json
```
Steps:
1. `scripts/fetch_hn.py`: every HN comment/story matching "youtube" or "youtu.be" from the Algolia HN API (date ranges split so each query stays under the 1000-hit cap) → `data/hn_raw.jsonl`
2. `scripts/aggregate.py`: pulls video IDs out of the links and counts distinct users, threads and years per video → `data/agg.json`
3. `scripts/metadata.py`: title, channel, length, views, category and embeddability from each watch page, cached in `data/meta_cache.json`
4. `scripts/build.py` → `site/videos.json`

## Run
```sh
python3 -m http.server 8777 -d site   # open http://localhost:8777
```
Likes, Watch later, playlists and history are stored in localStorage.
