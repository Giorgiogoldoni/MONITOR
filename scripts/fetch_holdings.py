#!/usr/bin/env python3
"""
RAPTOR ETF MONITOR — Holdings & CFTC Fetcher
Fetches holdings for: GMOM, RPAR, DBMF, AOA, AOR, MAGR, F701, F703
Fetches CFTC COT data weekly (Fridays)
Saves JSON snapshots to data/ directory
"""

import json
import os
import datetime
import requests
import csv
import io
import zipfile
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent
DATA = BASE / "data"

ETF_DIR  = DATA / "holdings"
CFTC_DIR = DATA / "cftc"

for d in [ETF_DIR, CFTC_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TODAY = datetime.date.today().isoformat()
WEEKDAY = datetime.date.today().weekday()  # 0=Mon … 6=Sun

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RAPTOR-ETF-Monitor/1.0)",
    "Accept": "text/html,application/json,text/csv,*/*",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ saved {path.relative_to(BASE)}")


def load_prev(etf: str) -> dict | None:
    folder = ETF_DIR / etf
    if not folder.exists():
        return None
    files = sorted(folder.glob("*.json"))
    if len(files) < 1:
        return None
    with open(files[-1]) as f:
        return json.load(f)


def already_done(etf: str) -> bool:
    return (ETF_DIR / etf / f"{TODAY}.json").exists()


def get(url: str, timeout=30) -> requests.Response:
    return requests.get(url, headers=HEADERS, timeout=timeout)


def parse_csv_text(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    return [row for row in reader]


# ── ETF Parsers ────────────────────────────────────────────────────────────────

def fetch_cambria(ticker: str, url: str) -> dict | None:
    """GMOM — Cambria daily holdings CSV"""
    try:
        r = get(url)
        r.raise_for_status()
        rows = parse_csv_text(r.text)
        holdings = []
        for row in rows:
            name   = row.get("Name") or row.get("Security Description") or ""
            ticker_h = row.get("Ticker") or row.get("Symbol") or ""
            weight = row.get("Weight (%)") or row.get("% of Net Assets") or "0"
            if name:
                holdings.append({
                    "name":   name.strip(),
                    "ticker": ticker_h.strip(),
                    "weight": float(str(weight).replace("%","").replace(",","").strip() or 0)
                })
        return {"date": TODAY, "source": url, "holdings": holdings}
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None


def fetch_ishares_usa(ticker: str, product_id: str) -> dict | None:
    """AOA, AOR — iShares USA holdings CSV"""
    url = f"https://www.ishares.com/us/products/{product_id}/fund.ajax.getChart.json"
    csv_url = f"https://www.ishares.com/us/products/{product_id}/_jcr_content/productDetail/productData.exportHoldings.csv/fund-holdings.csv"
    try:
        r = get(csv_url)
        r.raise_for_status()
        # Skip header rows until we find the data
        lines = r.text.splitlines()
        data_start = 0
        for i, line in enumerate(lines):
            if "Name" in line and "Weight" in line:
                data_start = i
                break
        text = "\n".join(lines[data_start:])
        rows = parse_csv_text(text)
        holdings = []
        for row in rows:
            name   = row.get("Name","").strip()
            ticker_h = row.get("Ticker","").strip()
            weight = row.get("Weight (%)","0")
            if name and ticker_h:
                try:
                    w = float(str(weight).replace("%","").replace(",","").strip())
                except:
                    w = 0.0
                holdings.append({"name": name, "ticker": ticker_h, "weight": w})
        return {"date": TODAY, "source": csv_url, "holdings": holdings}
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None


def fetch_evoke(ticker: str) -> dict | None:
    """RPAR, UPAR — Evoke Advisors holdings CSV"""
    urls = {
        "RPAR": "https://evokead.com/wp-content/uploads/rpar-daily-holdings.csv",
        "UPAR": "https://evokead.com/wp-content/uploads/upar-daily-holdings.csv",
    }
    url = urls.get(ticker, "")
    try:
        r = get(url)
        r.raise_for_status()
        rows = parse_csv_text(r.text)
        holdings = []
        for row in rows:
            name   = (row.get("Name") or row.get("Security") or "").strip()
            ticker_h = (row.get("Ticker") or row.get("Symbol") or "").strip()
            weight = row.get("Weight","0")
            if name:
                try:
                    w = float(str(weight).replace("%","").replace(",","").strip())
                except:
                    w = 0.0
                holdings.append({"name": name, "ticker": ticker_h, "weight": w})
        return {"date": TODAY, "source": url, "holdings": holdings}
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None


def fetch_imgp(ticker: str) -> dict | None:
    """DBMF — iMGP Funds holdings"""
    url = "https://imgpfunds.com/im-dbi-managed-futures-strategy-etf/"
    # iMGP publishes holdings as JSON endpoint
    api = "https://imgpfunds.com/wp-json/imgp/v1/fund-holdings?ticker=DBMF"
    try:
        r = get(api)
        if r.status_code == 200:
            data = r.json()
            holdings = []
            for item in data:
                holdings.append({
                    "name":   item.get("description",""),
                    "ticker": item.get("ticker",""),
                    "weight": float(item.get("weight",0))
                })
            return {"date": TODAY, "source": api, "holdings": holdings}
        # Fallback: scrape CSV if available
        csv_url = "https://imgpfunds.com/wp-content/uploads/dbmf-holdings.csv"
        r2 = get(csv_url)
        r2.raise_for_status()
        rows = parse_csv_text(r2.text)
        holdings = []
        for row in rows:
            name = (row.get("Name") or row.get("Security","")).strip()
            w    = float(str(row.get("Weight","0")).replace("%","") or 0)
            holdings.append({"name": name, "ticker": row.get("Ticker",""), "weight": w})
        return {"date": TODAY, "source": csv_url, "holdings": holdings}
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None


def fetch_blackrock_ucits(ticker: str, isin: str) -> dict | None:
    """MAGR — BlackRock UCITS holdings via iShares API"""
    url = f"https://www.ishares.com/uk/individual/en/products/etf-investments.ajax.getChart.json?productCode={isin}"
    csv_url = f"https://www.ishares.com/uk/individual/en/products/{isin}/_jcr_content/productDetail/productData.exportHoldings.csv/fund-holdings.csv"
    try:
        r = get(csv_url)
        r.raise_for_status()
        lines = r.text.splitlines()
        data_start = 0
        for i, line in enumerate(lines):
            if "Name" in line and "Weight" in line:
                data_start = i
                break
        text = "\n".join(lines[data_start:])
        rows = parse_csv_text(text)
        holdings = []
        for row in rows:
            name   = row.get("Name","").strip()
            ticker_h = row.get("Ticker","").strip()
            weight = row.get("Weight (%)","0")
            if name:
                try:
                    w = float(str(weight).replace("%","").replace(",","").strip())
                except:
                    w = 0.0
                holdings.append({"name": name, "ticker": ticker_h, "weight": w})
        return {"date": TODAY, "source": csv_url, "holdings": holdings}
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None


def fetch_amundi(ticker: str, isin: str) -> dict | None:
    """F701, F703 — Amundi holdings via extraETF or justETF scrape"""
    # Amundi publishes holdings on their site monthly — we use justETF API
    url = f"https://www.justetf.com/api/etfs/{isin}/holdings?locale=it&valuta=EUR"
    try:
        r = get(url)
        r.raise_for_status()
        data = r.json()
        holdings = []
        for item in data.get("holdings",[]):
            holdings.append({
                "name":   item.get("name",""),
                "ticker": item.get("symbol",""),
                "weight": float(item.get("weight",0))
            })
        return {"date": TODAY, "source": url, "holdings": holdings}
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None


# ── CFTC COT ───────────────────────────────────────────────────────────────────

COT_MARKETS = {
    "S&P 500":       "13874A",
    "Nasdaq 100":    "20974+",
    "Treasury 10Y":  "043602",
    "Treasury 2Y":   "042601",
    "Gold":          "088691",
    "Crude Oil":     "067651",
    "EUR/USD":       "099741",
    "Copper":        "085692",
}

def fetch_cftc() -> dict | None:
    """Download CFTC Traders in Financial Futures (TFF) report"""
    # CFTC publishes weekly ZIP with CSV
    year = datetime.date.today().year
    url = f"https://www.cftc.gov/dea/newcot/FinFutWk.zip"
    try:
        r = get(url, timeout=60)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            csv_name = [n for n in z.namelist() if n.endswith(".csv") or n.endswith(".txt")][0]
            with z.open(csv_name) as f:
                text = f.read().decode("utf-8", errors="replace")
        
        rows = parse_csv_text(text)
        results = {}
        
        for row in rows:
            cftc_code = row.get("CFTC_Contract_Market_Code","").strip()
            market_name = row.get("Market_and_Exchange_Names","").strip()
            
            for label, code in COT_MARKETS.items():
                if code in cftc_code or code in market_name:
                    try:
                        results[label] = {
                            "market": market_name,
                            "report_date": row.get("As_of_Date_In_Form_YYMMDD",""),
                            "lev_long":  int(str(row.get("Lev_Money_Positions_Long_All","0")).replace(",","")),
                            "lev_short": int(str(row.get("Lev_Money_Positions_Short_All","0")).replace(",","")),
                            "lev_net":   int(str(row.get("Lev_Money_Positions_Long_All","0")).replace(",","")) -
                                         int(str(row.get("Lev_Money_Positions_Short_All","0")).replace(",","")),
                            "asset_long":  int(str(row.get("Asset_Mgr_Positions_Long_All","0")).replace(",","")),
                            "asset_short": int(str(row.get("Asset_Mgr_Positions_Short_All","0")).replace(",","")),
                        }
                    except:
                        pass
        
        return {"date": TODAY, "source": url, "markets": results}
    except Exception as e:
        print(f"  ✗ CFTC: {e}")
        return None


# ── Main ───────────────────────────────────────────────────────────────────────

ETF_CONFIG = [
    # (ticker, frequency, fetch_fn)
    # frequency: 'daily' | 'weekly' | 'monthly'
    ("GMOM", "daily",   lambda: fetch_cambria("GMOM", "https://cambriafunds.com/wp-content/uploads/gmom-holdings.csv")),
    ("RPAR", "daily",   lambda: fetch_evoke("RPAR")),
    ("DBMF", "daily",   lambda: fetch_imgp("DBMF")),
    ("AOA",  "weekly",  lambda: fetch_ishares_usa("AOA", "239729")),
    ("AOR",  "weekly",  lambda: fetch_ishares_usa("AOR", "239756")),
    ("MAGR", "weekly",  lambda: fetch_blackrock_ucits("MAGR", "IE00BF1DX863")),
    ("F701", "monthly", lambda: fetch_amundi("F701", "DE000ETF7011")),
    ("F703", "monthly", lambda: fetch_amundi("F703", "DE000ETF7031")),
]

def should_fetch(frequency: str) -> bool:
    if frequency == "daily":
        return True
    if frequency == "weekly":
        return WEEKDAY == 0  # Monday
    if frequency == "monthly":
        return datetime.date.today().day == 1
    return False


def compute_strategic_delta(current: dict, prev: dict | None) -> list[dict]:
    """
    For each holding, compute weight delta.
    Returns list of significant changes (|delta| > 1.5%).
    """
    if not prev:
        return []
    prev_map = {h["ticker"]: h["weight"] for h in prev.get("holdings",[])}
    deltas = []
    for h in current.get("holdings",[]):
        t = h["ticker"]
        prev_w = prev_map.get(t, 0.0)
        delta = h["weight"] - prev_w
        if abs(delta) >= 1.5:
            deltas.append({
                "ticker": t,
                "name": h["name"],
                "prev_weight": round(prev_w, 4),
                "curr_weight": round(h["weight"], 4),
                "delta": round(delta, 4),
                "direction": "▲ AUMENTO" if delta > 0 else "▼ RIDUZIONE"
            })
    return sorted(deltas, key=lambda x: abs(x["delta"]), reverse=True)


def main():
    print(f"\n{'='*55}")
    print(f"  RAPTOR ETF MONITOR — {TODAY}")
    print(f"{'='*55}\n")

    # ETF Holdings
    for ticker, freq, fetch_fn in ETF_CONFIG:
        folder = ETF_DIR / ticker
        folder.mkdir(parents=True, exist_ok=True)
        out_path = folder / f"{TODAY}.json"

        if out_path.exists():
            print(f"  → {ticker}: già aggiornato oggi, skip")
            continue

        if not should_fetch(freq):
            print(f"  → {ticker}: non previsto oggi ({freq}), skip")
            continue

        print(f"  → Fetching {ticker} ({freq})...")
        data = fetch_fn()
        if data and data.get("holdings"):
            prev = load_prev(ticker)
            data["strategic_changes"] = compute_strategic_delta(data, prev)
            save_json(out_path, data)
        else:
            print(f"  ✗ {ticker}: nessun dato recuperato")

    # CFTC COT — ogni venerdì (weekday 4)
    print()
    cftc_path = CFTC_DIR / f"{TODAY}.json"
    if WEEKDAY == 4 and not cftc_path.exists():
        print("  → Fetching CFTC COT (venerdì)...")
        cot = fetch_cftc()
        if cot and cot.get("markets"):
            save_json(cftc_path, cot)
        else:
            print("  ✗ CFTC: nessun dato recuperato")
    else:
        if WEEKDAY != 4:
            print("  → CFTC: non è venerdì, skip")
        else:
            print("  → CFTC: già aggiornato oggi, skip")

    print(f"\n{'='*55}")
    print("  DONE")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
