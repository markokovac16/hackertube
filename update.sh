#!/bin/sh
set -e
D="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$D/data"
MIN_REC=${MIN_REC:-8}; MIN_YEARS=${MIN_YEARS:-3}
python3 "$D/scripts/fetch_hn.py" "$D/data/hn_raw.jsonl"
python3 "$D/scripts/aggregate.py" "$D/data/hn_raw.jsonl" "$D/data/agg.json"
python3 "$D/scripts/metadata.py" "$D/data/agg.json" "$D/data/meta_cache.json" "$MIN_REC" "$MIN_YEARS"
python3 "$D/scripts/build.py" "$D/data/agg.json" "$D/data/meta_cache.json" "$D/site/videos.json" "$MIN_REC" "$MIN_YEARS"
