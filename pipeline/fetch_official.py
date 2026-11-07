"""Indiana has no official restaurant list a script may read (official.py): nothing to fetch. Kept so the rebuild steps match the
family's; it writes an empty data/raw/official/meta.json."""
import json, os
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "official")
os.makedirs(OUT, exist_ok=True)
json.dump({}, open(os.path.join(OUT, "meta.json"), "w"))
print("Indiana: no official list fetched")
