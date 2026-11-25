#!/usr/bin/env python3
"""
Builds data/index.json — manifest of all available snapshots.
Called by GitHub Actions after fetch_holdings.py.
"""
import json
import datetime
from pathlib import Path

BASE  = Path(__file__).parent.parent
DATA  = BASE / "data"
ETF_DIR  = DATA / "holdings"
CFTC_DIR = DATA / "cftc"

index = {"etfs": {}, "cftc": []}

def valid_snapshot_date(stem):
    try:
        datetime.datetime.strptime(stem, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# ETF snapshots
for etf_folder in sorted(ETF_DIR.iterdir()):
    if not etf_folder.is_dir():
        continue
    ticker = etf_folder.name
    files  = sorted(f for f in etf_folder.glob("*.json") if valid_snapshot_date(f.stem))
    index["etfs"][ticker] = [f.stem for f in files]  # stems = dates

# CFTC snapshots
cftc_files = sorted(f for f in CFTC_DIR.glob("*.json") if valid_snapshot_date(f.stem))
index["cftc"] = [f.stem for f in cftc_files]

out = DATA / "index.json"
with open(out, "w") as f:
    json.dump(index, f, indent=2)

print(f"✓ index.json aggiornato — {sum(len(v) for v in index['etfs'].values())} snapshot ETF, {len(index['cftc'])} CFTC")
