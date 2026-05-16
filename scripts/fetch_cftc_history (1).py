#!/usr/bin/env python3
"""
RAPTOR ETF MONITOR — CFTC Historical Fetcher v2
Scarica gli archivi storici TFF + Disaggregated dal sito CFTC.gov.

I file ZIP contengono un foglio Excel (.xls) con tutti i report settimanali
dell'anno. Usa openpyxl/xlrd per leggerli.

Mercati:
  TFF (FinancialFutures): S&P500, Nasdaq, Treasury 2Y/10Y, EUR/USD
  Disaggregated:          Gold, Crude Oil, Copper (categoria Managed Money)
"""

import csv
import io
import json
import zipfile
import datetime
import requests
import struct
from pathlib import Path

BASE     = Path(__file__).parent.parent
CFTC_DIR = BASE / "data" / "cftc"
CFTC_DIR.mkdir(parents=True, exist_ok=True)

TODAY = datetime.date.today()

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; RAPTOR-ETF/4.0)"})

# ── Mercati TFF (Traders in Financial Futures) ─────────────────────────────────
TFF_MARKETS = {
    "S&P 500":      "13874A",
    "Nasdaq 100":   "20974+",
    "Treasury 10Y": "043602",
    "Treasury 2Y":  "042601",
    "EUR/USD":      "099741",
}

TFF_ALIASES = {
    "20974+": ["20974+", "20974P", "209740"],
}

# ── Mercati Disaggregated (Managed Money) ──────────────────────────────────────
DISAGG_MARKETS = {
    "Gold":      "088691",
    "Crude Oil": "067651",
    "Copper":    "085692",
}

DISAGG_ALIASES = {
    "067651": ["067651", "067652"],
}

def code_matches(cftc_code, target, aliases_dict):
    aliases = aliases_dict.get(target, [target])
    return any(a in cftc_code for a in aliases)

def parse_cftc_date(raw):
    raw = str(raw).strip()
    if len(raw) == 6 and raw.isdigit():
        return f"20{raw[:2]}-{raw[2:4]}-{raw[4:6]}"
    if len(raw) == 10 and "-" in raw:
        return raw
    return None

def to_int(s):
    try:
        return int(str(s).replace(",", "").strip())
    except:
        return 0

# ── Parse CSV TFF (colonne fisse, senza header) ────────────────────────────────
def parse_tff_csv(text):
    """
    Parsa FinFutWk.txt / storico TFF CSV.
    Colonne fisse:
      0  = Market name
      1  = Date YYMMDD
      3  = CFTC code
      12 = Asset Mgr Long
      13 = Asset Mgr Short
      15 = Lev Money Long
      16 = Lev Money Short
    """
    text = text.lstrip("\ufeff")
    reader = csv.reader(io.StringIO(text))
    snapshots = {}

    for cols in reader:
        if len(cols) < 17:
            continue
        market_name = cols[0].strip().strip('"')
        cftc_code   = cols[3].strip().strip('"')
        report_date = parse_cftc_date(cols[1].strip())
        if not report_date:
            continue

        for label, code in TFF_MARKETS.items():
            if code_matches(cftc_code, code, TFF_ALIASES) or code in market_name:
                if report_date not in snapshots:
                    snapshots[report_date] = {}
                if label not in snapshots[report_date]:
                    try:
                        ll = to_int(cols[15])
                        ls = to_int(cols[16])
                        snapshots[report_date][label] = {
                            "market":      market_name,
                            "report_date": report_date,
                            "lev_long":    ll,
                            "lev_short":   ls,
                            "lev_net":     ll - ls,
                            "asset_long":  to_int(cols[12]),
                            "asset_short": to_int(cols[13]),
                        }
                    except:
                        pass
    return snapshots

# ── Parse CSV Disaggregated (Gold/Crude/Copper) ────────────────────────────────
def parse_disagg_csv(text):
    """
    Parsa f_disagg.txt / storico Disaggregated CSV.
    Colonne fisse (Managed Money):
      0  = Market name
      1  = Date YYMMDD
      3  = CFTC code
      Long MM  = col 9
      Short MM = col 10
    """
    text = text.lstrip("\ufeff")
    reader = csv.reader(io.StringIO(text))
    snapshots = {}

    for cols in reader:
        if len(cols) < 12:
            continue
        market_name = cols[0].strip().strip('"')
        cftc_code   = cols[3].strip().strip('"')
        report_date = parse_cftc_date(cols[1].strip())
        if not report_date:
            continue

        for label, code in DISAGG_MARKETS.items():
            if code_matches(cftc_code, code, DISAGG_ALIASES) or code in market_name:
                if report_date not in snapshots:
                    snapshots[report_date] = {}
                if label not in snapshots[report_date]:
                    try:
                        ll = to_int(cols[9])
                        ls = to_int(cols[10])
                        snapshots[report_date][label] = {
                            "market":      market_name,
                            "report_date": report_date,
                            "lev_long":    ll,
                            "lev_short":   ls,
                            "lev_net":     ll - ls,
                            "asset_long":  0,
                            "asset_short": 0,
                        }
                    except:
                        pass
    return snapshots

# ── Download ZIP e estrai CSV ──────────────────────────────────────────────────
def fetch_zip_csv(url):
    """
    Scarica uno ZIP CFTC ed estrae il contenuto del primo file testuale.
    I file ZIP possono contenere .txt o .xls — restituiamo il testo se .txt,
    None se è solo .xls (non gestito senza dipendenze extra).
    """
    print(f"  → GET {url}")
    try:
        r = SESSION.get(url, timeout=120)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            names = z.namelist()
            print(f"    File nello ZIP: {names}")
            # Cerca file di testo/CSV
            txt = next((n for n in names if n.lower().endswith(('.txt', '.csv'))), None)
            if txt:
                with z.open(txt) as f:
                    return f.read().decode("utf-8", errors="replace")
            print(f"    ✗ nessun file .txt/.csv nello ZIP (trovati: {names})")
            return None
    except Exception as e:
        print(f"    ✗ {e}")
        return None

def fetch_url_direct(url):
    """Scarica un file TXT diretto."""
    print(f"  → GET {url}")
    try:
        r = SESSION.get(url, timeout=60)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"    ✗ {e}")
        return None

# ── Merge e salvataggio snapshot ───────────────────────────────────────────────
def merge_and_save(tff_snaps, disagg_snaps, source):
    """
    Unisce i dati TFF e Disaggregated per data e salva i JSON.
    """
    all_dates = set(list(tff_snaps.keys()) + list(disagg_snaps.keys()))
    saved = skipped = 0

    for date in sorted(all_dates):
        out_path = CFTC_DIR / f"{date}.json"
        markets = {}

        # Carica esistente se già presente (per merge)
        if out_path.exists():
            try:
                existing = json.loads(out_path.read_text(encoding="utf-8"))
                markets = existing.get("markets", {})
            except:
                pass

        # Aggiunge dati TFF
        for label, data in tff_snaps.get(date, {}).items():
            if label not in markets:
                markets[label] = data

        # Aggiunge dati Disaggregated
        for label, data in disagg_snaps.get(date, {}).items():
            if label not in markets:
                markets[label] = data

        if not markets:
            continue

        new_data = {"date": date, "source": source, "markets": markets}

        # Salta solo se il file esiste E ha già tutti i mercati
        if out_path.exists() and len(markets) >= len(TFF_MARKETS) + len(DISAGG_MARKETS):
            skipped += 1
            continue

        out_path.write_text(
            json.dumps(new_data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        saved += 1

    return saved, skipped

# ── URL storici CFTC ───────────────────────────────────────────────────────────
def get_historical_urls(year):
    """Restituisce le URL per TFF e Disaggregated di un anno."""
    return {
        "tff":    f"https://www.cftc.gov/files/dea/history/fut_fin_xls_{year}.zip",
        "disagg": f"https://www.cftc.gov/files/dea/history/fut_disagg_xls_{year}.zip",
        # Formato alternativo TXT (alcuni anni)
        "tff_txt":    f"https://www.cftc.gov/files/dea/history/fin_fut_{year}.zip",
        "disagg_txt": f"https://www.cftc.gov/files/dea/history/disagg_fut_{year}.zip",
    }

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*55}")
    print(f"  CFTC HISTORICAL FETCH v2 — {TODAY}")
    print(f"{'='*55}\n")

    existing = list(CFTC_DIR.glob("*.json"))
    print(f"  File esistenti: {len(existing)}\n")

    total_saved = total_skipped = 0
    current_year = TODAY.year

    for year in range(2022, current_year):
        print(f"\n── Anno {year} ──")
        urls = get_historical_urls(year)

        # TFF
        tff_snaps = {}
        for key in ["tff", "tff_txt"]:
            text = fetch_zip_csv(urls[key])
            if text:
                tff_snaps = parse_tff_csv(text)
                print(f"    TFF: {len(tff_snaps)} settimane")
                break

        # Disaggregated
        disagg_snaps = {}
        for key in ["disagg", "disagg_txt"]:
            text = fetch_zip_csv(urls[key])
            if text:
                disagg_snaps = parse_disagg_csv(text)
                print(f"    Disagg: {len(disagg_snaps)} settimane")
                break

        if tff_snaps or disagg_snaps:
            saved, skipped = merge_and_save(
                tff_snaps, disagg_snaps,
                f"CFTC historical {year}"
            )
            print(f"    → Salvati: {saved} · Skip: {skipped}")
            total_saved   += saved
            total_skipped += skipped

    # Anno corrente: file settimanali diretti
    print(f"\n── Anno corrente ({current_year}) ──")

    tff_text    = fetch_url_direct("https://www.cftc.gov/dea/newcot/FinFutWk.txt")
    disagg_text = fetch_url_direct("https://www.cftc.gov/dea/newcot/fut_disagg.txt")

    tff_snaps    = parse_tff_csv(tff_text)       if tff_text    else {}
    disagg_snaps = parse_disagg_csv(disagg_text) if disagg_text else {}

    print(f"    TFF corrente: {len(tff_snaps)} settimane")
    print(f"    Disagg corrente: {len(disagg_snaps)} settimane")

    if tff_snaps or disagg_snaps:
        saved, skipped = merge_and_save(tff_snaps, disagg_snaps, "CFTC.gov current")
        print(f"    → Salvati: {saved} · Skip: {skipped}")
        total_saved   += saved
        total_skipped += skipped

    total = list(CFTC_DIR.glob("*.json"))
    print(f"\n{'='*55}")
    print(f"  DONE — Nuovi: {total_saved} · Skip: {total_skipped} · Totale: {len(total)}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    main()
