#!/usr/bin/env python3
"""
RAPTOR ETF MONITOR — CFTC Historical Fetcher
Scarica gli archivi storici TFF dal sito CFTC.gov e popola data/cftc/
con un JSON per ogni settimana disponibile.

Eseguito automaticamente dal workflow se data/cftc/ ha meno di 10 file.
Anni scaricati: 2022, 2023, 2024, 2025, 2026 (corrente via FinFutWk.txt)
"""

import csv
import io
import json
import zipfile
import datetime
import requests
from pathlib import Path

BASE     = Path(__file__).parent.parent
CFTC_DIR = BASE / "data" / "cftc"
CFTC_DIR.mkdir(parents=True, exist_ok=True)

TODAY = datetime.date.today()

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; RAPTOR-ETF/4.0)"})

COT_MARKETS = {
    "S&P 500":      "13874A",
    "Nasdaq 100":   "20974+",
    "Treasury 10Y": "043602",
    "Treasury 2Y":  "042601",
    "Gold":         "088691",
    "Crude Oil":    "067651",
    "EUR/USD":      "099741",
    "Copper":       "085692",
}

COT_ALIASES = {
    "20974+": ["20974+", "20974P", "209740"],
    "067651": ["067651", "067652"],
}

def code_matches(cftc_code, target):
    return any(a in cftc_code for a in COT_ALIASES.get(target, [target]))

def parse_cftc_date(raw):
    raw = str(raw).strip()
    if len(raw) == 6 and raw.isdigit():
        yy, mm, dd = raw[:2], raw[2:4], raw[4:6]
        return f"20{yy}-{mm}-{dd}"
    if len(raw) == 10 and "-" in raw:
        return raw
    return None

def to_int(s):
    try:
        return int(str(s).replace(",", "").strip())
    except:
        return 0

def parse_tff_csv(text):
    """
    Parsa un file TFF CSV (senza header, colonne fisse).
    Restituisce dict: { 'YYYY-MM-DD': { markets: {...} } }
    """
    text = text.lstrip("\ufeff")
    reader = csv.reader(io.StringIO(text))
    snapshots = {}  # date -> { label -> data }

    for cols in reader:
        if len(cols) < 17:
            continue
        market_name = cols[0].strip().strip('"')
        cftc_code   = cols[3].strip().strip('"')
        report_date = parse_cftc_date(cols[1].strip())
        if not report_date:
            continue

        for label, code in COT_MARKETS.items():
            if code_matches(cftc_code, code) or code in market_name:
                if report_date not in snapshots:
                    snapshots[report_date] = {}
                if label not in snapshots[report_date]:
                    try:
                        ll  = to_int(cols[15])
                        ls  = to_int(cols[16])
                        al  = to_int(cols[12])
                        as_ = to_int(cols[13])
                        snapshots[report_date][label] = {
                            "market":      market_name,
                            "report_date": report_date,
                            "lev_long":    ll,
                            "lev_short":   ls,
                            "lev_net":     ll - ls,
                            "asset_long":  al,
                            "asset_short": as_,
                        }
                    except:
                        pass
    return snapshots

def fetch_year_zip(year):
    """Scarica il file ZIP annuale CFTC e restituisce il testo CSV."""
    # URL formato storico CFTC
    url = f"https://www.cftc.gov/files/dea/history/fut_fin_xls_{year}.zip"
    print(f"  → Scarico {year}: {url}")
    try:
        r = SESSION.get(url, timeout=120)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            # Cerca il file TXT/CSV dentro lo ZIP
            names = z.namelist()
            csv_name = next(
                (n for n in names if n.lower().endswith(('.txt', '.csv'))),
                None
            )
            if not csv_name:
                print(f"    ✗ nessun CSV nello ZIP {year}")
                return None
            with z.open(csv_name) as f:
                return f.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"    ✗ {year}: {e}")
        return None

def fetch_current_week():
    """Scarica il report corrente da FinFutWk.txt."""
    url = "https://www.cftc.gov/dea/newcot/FinFutWk.txt"
    print(f"  → Scarico settimana corrente: {url}")
    try:
        r = SESSION.get(url, timeout=60)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"    ✗ {e}")
        return None

def save_snapshots(snapshots, source):
    """Salva ogni snapshot come JSON in data/cftc/YYYY-MM-DD.json"""
    saved = 0
    skipped = 0
    for date, markets in snapshots.items():
        if not markets:
            continue
        out_path = CFTC_DIR / f"{date}.json"
        if out_path.exists():
            skipped += 1
            continue
        data = {
            "date":    date,
            "source":  source,
            "markets": markets,
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        saved += 1
    return saved, skipped

def main():
    print(f"\n{'='*55}")
    print(f"  CFTC HISTORICAL FETCH — {TODAY}")
    print(f"{'='*55}\n")

    existing = list(CFTC_DIR.glob("*.json"))
    print(f"  File esistenti in data/cftc/: {len(existing)}\n")

    total_saved   = 0
    total_skipped = 0

    # Anni storici: dal 2022 all'anno corrente
    current_year = TODAY.year
    years = list(range(2022, current_year))  # anni completi

    for year in years:
        text = fetch_year_zip(year)
        if not text:
            continue
        snapshots = parse_tff_csv(text)
        saved, skipped = save_snapshots(snapshots, f"CFTC historical {year}")
        print(f"    → {year}: {len(snapshots)} settimane · salvati: {saved} · skip: {skipped}")
        total_saved   += saved
        total_skipped += skipped

    # Anno corrente via file settimanale (ha solo la settimana più recente)
    text = fetch_current_week()
    if text:
        snapshots = parse_tff_csv(text)
        saved, skipped = save_snapshots(snapshots, "CFTC.gov FinFutWk.txt")
        print(f"    → corrente: {len(snapshots)} settimane · salvati: {saved} · skip: {skipped}")
        total_saved   += saved
        total_skipped += skipped

    total = list(CFTC_DIR.glob("*.json"))
    print(f"\n{'='*55}")
    print(f"  DONE — Nuovi: {total_saved} · Skip: {total_skipped} · Totale: {len(total)}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    main()
