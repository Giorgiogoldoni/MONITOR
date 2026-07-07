#!/usr/bin/env python3
"""
Builds data/index.json — manifest of all available snapshots.
Called by GitHub Actions after fetch_holdings.py.
"""
import json
from pathlib import Path

BASE  = Path(__file__).parent.parent
DATA  = BASE / "data"
ETF_DIR  = DATA / "holdings"
CFTC_DIR = DATA / "cftc"

index = {"etfs": {}, "cftc": []}

# ETF snapshots
for etf_folder in sorted(ETF_DIR.iterdir()):
    if not etf_folder.is_dir():
        continue
    ticker = etf_folder.name
    files  = sorted(etf_folder.glob("*.json"))
    index["etfs"][ticker] = [f.stem for f in files]  # stems = dates

# CFTC snapshots
cftc_files = sorted(CFTC_DIR.glob("*.json"))
index["cftc"] = [f.stem for f in cftc_files]

import os
# Inietta GH_TOKEN dal secret GitHub Actions (mai visibile nel codice)
gh_token = os.environ.get("GH_TOKEN", "")
if gh_token:
    index["_gh_token"] = gh_token

out = DATA / "index.json"
with open(out, "w") as f:
    json.dump(index, f, indent=2)

print(f"✓ index.json aggiornato — {sum(len(v) for v in index['etfs'].values())} snapshot ETF, {len(index['cftc'])} CFTC")
