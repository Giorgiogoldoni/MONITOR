#!/usr/bin/env python3
"""
RAPTOR ETF MONITOR — CFTC Historical Fetcher v3
Legge i file XLS dagli ZIP storici CFTC:
  TFF:         fut_fin_xls_YYYY.zip  → FinFutYY.xls
  Disagg:      fut_disagg_xls_YYYY.zip → f_year.xls
  Corrente TFF: FinFutWk.txt (CSV)
  Corrente Disagg: f_disagg.txt (CSV)
"""

import csv
import io
import json
import zipfile
import datetime
import requests
from pathlib import Path

import xlrd  # pip install xlrd

BASE     = Path(__file__).parent.parent
CFTC_DIR = BASE / "data" / "cftc"
CFTC_DIR.mkdir(parents=True, exist_ok=True)

TODAY = datetime.date.today()

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; RAPTOR-ETF/4.0)"})

# ── Mercati TFF ────────────────────────────────────────────────────────────────
TFF_MARKETS = {
    "S&P 500":      "13874A",
    "Nasdaq 100":   "20974+",
    "Treasury 10Y": "043602",
    "Treasury 2Y":  "042601",
    "EUR/USD":      "099741",
}
TFF_ALIASES = {"20974+": ["20974+", "20974P", "209740"]}

# ── Mercati Disaggregated (Managed Money) ──────────────────────────────────────
DISAGG_MARKETS = {
    "Gold":      "088691",
    "Crude Oil": "067651",
    "Copper":    "085692",
}
DISAGG_ALIASES = {"067651": ["067651", "067652"]}

def code_matches(code, target, aliases):
    return any(a in code for a in aliases.get(target, [target]))

def parse_date(raw):
    raw = str(raw).strip()
    if len(raw) == 6 and raw.isdigit():
        return f"20{raw[:2]}-{raw[2:4]}-{raw[4:6]}"
    if len(raw) == 10 and "-" in raw:
        return raw
    # Formato Excel numerico (giorni dal 1900)
    try:
        f = float(raw)
        if f > 1000:
            d = xlrd.xldate_as_datetime(f, 0)
            return d.strftime("%Y-%m-%d")
    except:
        pass
    return None

def to_int(v):
    try:
        return int(float(str(v).replace(",", "").strip()))
    except:
        return 0

# ── Parser XLS TFF ─────────────────────────────────────────────────────────────
def parse_tff_xls(xls_bytes):
    """
    Legge FinFutYY.xls — stesse colonne del CSV:
    col 0 = market name, col 1 = date, col 3 = CFTC code
    col 12 = asset long, col 13 = asset short
    col 15 = lev long,   col 16 = lev short
    """
    snapshots = {}
    try:
        wb = xlrd.open_workbook(file_contents=xls_bytes)
        ws = wb.sheet_by_index(0)
        for rx in range(ws.nrows):
            row = ws.row_values(rx)
            if len(row) < 17:
                continue
            market_name = str(row[0]).strip().strip('"')
            cftc_code   = str(row[3]).strip().strip('"')
            report_date = parse_date(str(row[1]).strip())
            if not report_date:
                continue
            for label, code in TFF_MARKETS.items():
                if code_matches(cftc_code, code, TFF_ALIASES) or code in market_name:
                    if report_date not in snapshots:
                        snapshots[report_date] = {}
                    if label not in snapshots[report_date]:
                        ll = to_int(row[15])
                        ls = to_int(row[16])
                        snapshots[report_date][label] = {
                            "market":      market_name,
                            "report_date": report_date,
                            "lev_long":    ll,
                            "lev_short":   ls,
                            "lev_net":     ll - ls,
                            "asset_long":  to_int(row[12]),
                            "asset_short": to_int(row[13]),
                        }
    except Exception as e:
        print(f"    ✗ parse XLS TFF: {e}")
    return snapshots

# ── Parser XLS Disaggregated ───────────────────────────────────────────────────
def parse_disagg_xls(xls_bytes):
    """
    Legge f_year.xls — Managed Money:
    col 0 = market, col 1 = date, col 3 = code
    col 9 = MM long, col 10 = MM short
    """
    snapshots = {}
    try:
        wb = xlrd.open_workbook(file_contents=xls_bytes)
        ws = wb.sheet_by_index(0)
        for rx in range(ws.nrows):
            row = ws.row_values(rx)
            if len(row) < 12:
                continue
            market_name = str(row[0]).strip().strip('"')
            cftc_code   = str(row[3]).strip().strip('"')
            report_date = parse_date(str(row[1]).strip())
            if not report_date:
                continue
            for label, code in DISAGG_MARKETS.items():
                if code_matches(cftc_code, code, DISAGG_ALIASES) or code in market_name:
                    if report_date not in snapshots:
                        snapshots[report_date] = {}
                    if label not in snapshots[report_date]:
                        ll = to_int(row[9])
                        ls = to_int(row[10])
                        snapshots[report_date][label] = {
                            "market":      market_name,
                            "report_date": report_date,
                            "lev_long":    ll,
                            "lev_short":   ls,
                            "lev_net":     ll - ls,
                            "asset_long":  0,
                            "asset_short": 0,
                        }
    except Exception as e:
        print(f"    ✗ parse XLS Disagg: {e}")
    return snapshots

# ── Parser CSV TFF (file corrente) ─────────────────────────────────────────────
def parse_tff_csv(text):
    text = text.lstrip("\ufeff")
    reader = csv.reader(io.StringIO(text))
    snapshots = {}
    for cols in reader:
        if len(cols) < 17:
            continue
        market_name = cols[0].strip().strip('"')
        cftc_code   = cols[3].strip().strip('"')
        report_date = parse_date(cols[1].strip())
        if not report_date:
            continue
        for label, code in TFF_MARKETS.items():
            if code_matches(cftc_code, code, TFF_ALIASES) or code in market_name:
                if report_date not in snapshots:
                    snapshots[report_date] = {}
                if label not in snapshots[report_date]:
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
    return snapshots

# ── Parser CSV Disaggregated (file corrente) ───────────────────────────────────
def parse_disagg_csv(text):
    text = text.lstrip("\ufeff")
    reader = csv.reader(io.StringIO(text))
    snapshots = {}
    for cols in reader:
        if len(cols) < 12:
            continue
        market_name = cols[0].strip().strip('"')
        cftc_code   = cols[3].strip().strip('"')
        report_date = parse_date(cols[1].strip())
        if not report_date:
            continue
        for label, code in DISAGG_MARKETS.items():
            if code_matches(cftc_code, code, DISAGG_ALIASES) or code in market_name:
                if report_date not in snapshots:
                    snapshots[report_date] = {}
                if label not in snapshots[report_date]:
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
    return snapshots

# ── Download ───────────────────────────────────────────────────────────────────
def fetch_zip_xls(url, xls_name):
    print(f"  → GET {url}")
    try:
        r = SESSION.get(url, timeout=120)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            names = z.namelist()
            target = next((n for n in names if n.lower().endswith('.xls')), None)
            if not target:
                print(f"    ✗ nessun XLS nello ZIP (trovati: {names})")
                return None
            with z.open(target) as f:
                return f.read()
    except Exception as e:
        print(f"    ✗ {e}")
        return None

def fetch_text(url):
    print(f"  → GET {url}")
    try:
        r = SESSION.get(url, timeout=60)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"    ✗ {e}")
        return None

# ── Salvataggio ────────────────────────────────────────────────────────────────
def merge_and_save(tff_snaps, disagg_snaps, source):
    all_dates = set(list(tff_snaps.keys()) + list(disagg_snaps.keys()))
    saved = skipped = 0
    for date in sorted(all_dates):
        out_path = CFTC_DIR / f"{date}.json"
        markets = {}
        if out_path.exists():
            try:
                existing = json.loads(out_path.read_text(encoding="utf-8"))
                markets = existing.get("markets", {})
                # Se ha già tutti e 8 i mercati salta
                if len(markets) >= 8:
                    skipped += 1
                    continue
            except:
                pass
        for label, data in tff_snaps.get(date, {}).items():
            if label not in markets:
                markets[label] = data
        for label, data in disagg_snaps.get(date, {}).items():
            if label not in markets:
                markets[label] = data
        if not markets:
            continue
        out_path.write_text(
            json.dumps({"date": date, "source": source, "markets": markets},
                       indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        saved += 1
    return saved, skipped

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*55}")
    print(f"  CFTC HISTORICAL FETCH v3 — {TODAY}")
    print(f"{'='*55}\n")

    existing = list(CFTC_DIR.glob("*.json"))
    print(f"  File esistenti: {len(existing)}\n")

    total_saved = total_skipped = 0
    current_year = TODAY.year

    # ── Anni storici ──────────────────────────────────────────────────────────
    for year in range(2022, current_year):
        print(f"\n── Anno {year} ──")

        # TFF XLS
        tff_bytes = fetch_zip_xls(
            f"https://www.cftc.gov/files/dea/history/fut_fin_xls_{year}.zip",
            "FinFutYY.xls"
        )
        tff_snaps = parse_tff_xls(tff_bytes) if tff_bytes else {}
        print(f"    TFF: {len(tff_snaps)} settimane")

        # Disaggregated XLS
        disagg_bytes = fetch_zip_xls(
            f"https://www.cftc.gov/files/dea/history/fut_disagg_xls_{year}.zip",
            "f_year.xls"
        )
        disagg_snaps = parse_disagg_xls(disagg_bytes) if disagg_bytes else {}
        print(f"    Disagg: {len(disagg_snaps)} settimane")

        if tff_snaps or disagg_snaps:
            saved, skipped = merge_and_save(tff_snaps, disagg_snaps, f"CFTC {year}")
            print(f"    → Salvati: {saved} · Skip: {skipped}")
            total_saved   += saved
            total_skipped += skipped

    # ── Anno corrente (CSV settimanale) ───────────────────────────────────────
    print(f"\n── Anno corrente ({current_year}) ──")

    tff_text = fetch_text("https://www.cftc.gov/dea/newcot/FinFutWk.txt")
    tff_snaps = parse_tff_csv(tff_text) if tff_text else {}

    # Disaggregated corrente — prova URL alternative
    disagg_snaps = {}
    for url in [
        "https://www.cftc.gov/dea/newcot/fut_disagg.txt",
        "https://www.cftc.gov/dea/newcot/f_disagg.txt",
        "https://www.cftc.gov/dea/newcot/dea_fut_disagg_txt_2026.zip",
    ]:
        text = fetch_text(url)
        if text and len(text) > 500:
            disagg_snaps = parse_disagg_csv(text)
            if disagg_snaps:
                break

    print(f"    TFF corrente: {len(tff_snaps)} settimane")
    print(f"    Disagg corrente: {len(disagg_snaps)} settimane")

    if tff_snaps or disagg_snaps:
        saved, skipped = merge_and_save(tff_snaps, disagg_snaps, "CFTC current")
        print(f"    → Salvati: {saved} · Skip: {skipped}")
        total_saved   += saved
        total_skipped += skipped

    total = list(CFTC_DIR.glob("*.json"))
    print(f"\n{'='*55}")
    print(f"  DONE — Nuovi: {total_saved} · Skip: {total_skipped} · Totale: {len(total)}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    main()
