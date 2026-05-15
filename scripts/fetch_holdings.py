#!/usr/bin/env python3
"""
RAPTOR ETF MONITOR — Holdings & CFTC Fetcher v2
Frequenza: settimanale (lunedì) + manuale

ETF USA  (GMOM, RPAR, DBMF, AOA, AOR) → ETF.com scraping
ETF UCITS (MAGR, F701, F703)           → investing.com via Playwright
CFTC COT                               → CFTC.gov ZIP (venerdì)
"""

import json
import os
import sys
import datetime
import time
import csv
import io
import zipfile
import re
from pathlib import Path

import requests

# Playwright importato solo se necessario
_pw_available = False
try:
    from playwright.sync_api import sync_playwright
    _pw_available = True
except ImportError:
    pass

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE     = Path(__file__).parent.parent
DATA     = BASE / "data"
ETF_DIR  = DATA / "holdings"
CFTC_DIR = DATA / "cftc"

for d in [ETF_DIR, CFTC_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TODAY   = datetime.date.today().isoformat()
WEEKDAY = datetime.date.today().weekday()  # 0=Mon … 6=Sun

# ── HTTP helpers ───────────────────────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
})


def get(url: str, timeout: int = 30) -> requests.Response:
    time.sleep(1)  # cortesia verso i server
    return SESSION.get(url, timeout=timeout)


def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ salvato {path.relative_to(BASE)}")


def load_prev(etf: str) -> dict | None:
    folder = ETF_DIR / etf
    if not folder.exists():
        return None
    files = sorted(folder.glob("*.json"))
    if not files:
        return None
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


def already_done(etf: str) -> bool:
    return (ETF_DIR / etf / f"{TODAY}.json").exists()


def parse_float(s: str) -> float:
    try:
        return float(str(s).replace("%", "").replace(",", ".").strip())
    except Exception:
        return 0.0


# ── ETF.com scraper (USA ETF) ──────────────────────────────────────────────────

ETFCOM_SLUGS = {
    "GMOM": "GMOM",
    "RPAR": "RPAR",
    "DBMF": "DBMF",
    "AOA":  "AOA",
    "AOR":  "AOR",
}


def fetch_etfcom(ticker: str) -> dict | None:
    """
    Scarica holdings da ETF.com.
    URL: https://www.etf.com/TICKER  — la tabella holdings è in #holdings-tab
    """
    url = f"https://www.etf.com/{ticker}"
    print(f"    GET {url}")
    try:
        r = get(url)
        if r.status_code != 200:
            print(f"    ✗ HTTP {r.status_code}")
            return None

        text = r.text

        # ETF.com renderizza holdings in una <table> con class "holdings"
        # Cerchiamo righe <tr> dentro quella tabella
        # Pattern: <td ...>Name</td><td ...>Ticker</td><td ...>Weight</td>
        # La tabella ha id="holdings-tab" o class contenente "holdings"

        # Troviamo il blocco tabella holdings
        table_match = re.search(
            r'<table[^>]*(?:id="holdings"|class="[^"]*holding[^"]*")[^>]*>(.*?)</table>',
            text, re.DOTALL | re.IGNORECASE
        )

        if not table_match:
            # Fallback: cerca qualsiasi tabella con colonna "Weight"
            tables = re.findall(r'<table[^>]*>(.*?)</table>', text, re.DOTALL | re.IGNORECASE)
            table_match_text = None
            for t in tables:
                if "Weight" in t or "weight" in t:
                    table_match_text = t
                    break
        else:
            table_match_text = table_match.group(1)

        if not table_match_text:
            print(f"    ✗ tabella holdings non trovata in ETF.com/{ticker}")
            return None

        # Estrai righe
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_match_text, re.DOTALL | re.IGNORECASE)
        holdings = []
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            # Rimuovi tag HTML interni
            cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            if len(cells) < 2:
                continue
            # ETF.com: col 0=Name, col 1=Weight (o col 0=%, col 1=Name)
            # Proviamo a individuare la colonna peso cercando il simbolo %
            weight_col = None
            for i, c in enumerate(cells):
                if "%" in c:
                    weight_col = i
                    break
            if weight_col is None:
                continue
            name_col = 0 if weight_col != 0 else 1
            if name_col >= len(cells):
                continue
            name   = cells[name_col].strip()
            weight = parse_float(cells[weight_col])
            if not name or name.lower() in ("name", "holding", "security", ""):
                continue
            if weight == 0:
                continue
            # Ticker: se c'è una terza colonna breve, è il ticker
            ticker_h = ""
            for i, c in enumerate(cells):
                if i != name_col and i != weight_col and len(c) <= 6 and c.isupper():
                    ticker_h = c
                    break
            holdings.append({"name": name, "ticker": ticker_h, "weight": weight})

        if not holdings:
            print(f"    ✗ nessuna holding estratta da ETF.com/{ticker}")
            return None

        print(f"    → {len(holdings)} holdings trovate")
        return {"date": TODAY, "source": url, "holdings": holdings}

    except Exception as e:
        print(f"    ✗ eccezione: {e}")
        return None


# ── Investing.com scraper via Playwright (UCITS ETF) ──────────────────────────

INVESTING_URLS = {
    "MAGR": "https://it.investing.com/etfs/magr-holdings?cid=1208413",
    "F701": "https://it.investing.com/etfs/comstage-vermogensstrategie-holdings",
    "F703": "https://it.investing.com/etfs/f703-holdings",
}


def fetch_investing_playwright(ticker: str) -> dict | None:
    """
    Usa Playwright (Chromium headless) per caricare la pagina investing.com
    e estrarre la tabella holdings — bypassa Cloudflare.
    """
    if not _pw_available:
        print(f"    ✗ Playwright non installato")
        return None

    url = INVESTING_URLS[ticker]
    print(f"    Playwright → {url}")

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="it-IT",
                viewport={"width": 1280, "height": 900},
            )
            page = ctx.new_page()

            # Blocca risorse inutili per velocizzare
            page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda r: r.abort())

            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Accetta cookie se appare il banner
            try:
                page.click("button#onetrust-accept-btn-handler", timeout=5000)
                page.wait_for_timeout(1000)
            except Exception:
                pass

            # Aspetta la tabella holdings
            try:
                page.wait_for_selector("table", timeout=15000)
            except Exception:
                print(f"    ✗ tabella non trovata entro timeout")
                browser.close()
                return None

            # Estrai HTML della pagina
            html = page.content()
            browser.close()

        # Parse tabella holdings dall'HTML
        # Investing.com: tabella con thead Name / % of portfolio (o simile)
        tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)

        holdings = []
        for table in tables:
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL | re.IGNORECASE)
            if len(rows) < 3:
                continue
            for row in rows[1:]:  # salta header
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
                cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
                if len(cells) < 2:
                    continue
                # Cerca cella con %
                weight_col = None
                for i, c in enumerate(cells):
                    if "%" in c:
                        weight_col = i
                        break
                if weight_col is None:
                    continue
                name = cells[0].strip()
                if not name or name.lower() in ("name", "holding", "asset", ""):
                    continue
                weight = parse_float(cells[weight_col])
                if weight == 0:
                    continue
                holdings.append({"name": name, "ticker": "", "weight": weight})

            if holdings:
                break  # trovata la tabella giusta

        if not holdings:
            print(f"    ✗ nessuna holding estratta da investing.com per {ticker}")
            return None

        print(f"    → {len(holdings)} holdings trovate")
        return {"date": TODAY, "source": url, "holdings": holdings}

    except Exception as e:
        print(f"    ✗ eccezione Playwright: {e}")
        return None


# ── CFTC COT ───────────────────────────────────────────────────────────────────

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

# Alcuni codici appaiono con varianti nel CSV CFTC
COT_ALIASES = {
    "20974+": ["20974+", "20974P", "209740"],
}


def code_matches(cftc_code: str, target: str) -> bool:
    aliases = COT_ALIASES.get(target, [target])
    return any(a in cftc_code for a in aliases)


def fetch_cftc() -> dict | None:
    url = "https://www.cftc.gov/dea/newcot/FinFutWk.zip"
    print(f"    GET {url}")
    try:
        r = get(url, timeout=90)
        r.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            csv_name = next(
                (n for n in z.namelist() if n.lower().endswith((".csv", ".txt"))),
                None
            )
            if not csv_name:
                print("    ✗ nessun CSV nel ZIP CFTC")
                return None
            with z.open(csv_name) as f:
                text = f.read().decode("utf-8", errors="replace")

        # Rimuovi BOM se presente
        text = text.lstrip("\ufeff")

        reader = csv.DictReader(io.StringIO(text))
        results = {}

        for row in reader:
            cftc_code = row.get("CFTC_Contract_Market_Code", "").strip()
            market_name = row.get("Market_and_Exchange_Names", "").strip()

            for label, code in COT_MARKETS.items():
                if code_matches(cftc_code, code) or code in market_name:
                    try:
                        lev_long  = int(str(row.get("Lev_Money_Positions_Long_All",  "0")).replace(",", ""))
                        lev_short = int(str(row.get("Lev_Money_Positions_Short_All", "0")).replace(",", ""))
                        results[label] = {
                            "market":       market_name,
                            "report_date":  row.get("As_of_Date_In_Form_YYMMDD", ""),
                            "lev_long":     lev_long,
                            "lev_short":    lev_short,
                            "lev_net":      lev_long - lev_short,
                            "asset_long":   int(str(row.get("Asset_Mgr_Positions_Long_All",  "0")).replace(",", "")),
                            "asset_short":  int(str(row.get("Asset_Mgr_Positions_Short_All", "0")).replace(",", "")),
                        }
                    except Exception as ex:
                        print(f"    ✗ parse CFTC row '{label}': {ex}")

        if not results:
            print("    ✗ nessun mercato trovato nel CSV CFTC")
            return None

        print(f"    → {len(results)}/{len(COT_MARKETS)} mercati trovati")
        return {"date": TODAY, "source": url, "markets": results}

    except Exception as e:
        print(f"    ✗ eccezione CFTC: {e}")
        return None


# ── Strategic delta ────────────────────────────────────────────────────────────

def compute_strategic_delta(current: dict, prev: dict | None) -> list[dict]:
    if not prev:
        return []
    # Usa ticker se disponibile, altrimenti name come chiave
    def key(h):
        return (h.get("ticker") or h.get("name", "")).strip()

    prev_map = {key(h): h["weight"] for h in prev.get("holdings", []) if key(h)}
    deltas = []
    for h in current.get("holdings", []):
        k = key(h)
        if not k:
            continue
        prev_w = prev_map.get(k, 0.0)
        delta  = h["weight"] - prev_w
        if abs(delta) >= 1.5:
            deltas.append({
                "ticker":      h.get("ticker", ""),
                "name":        h.get("name", k),
                "prev_weight": round(prev_w, 4),
                "curr_weight": round(h["weight"], 4),
                "delta":       round(delta, 4),
                "direction":   "▲ AUMENTO" if delta > 0 else "▼ RIDUZIONE",
            })
    return sorted(deltas, key=lambda x: abs(x["delta"]), reverse=True)


# ── ETF config ─────────────────────────────────────────────────────────────────

ETF_CONFIG = [
    # (ticker, fetch_fn)
    # Tutti settimanali — il workflow gira ogni lunedì
    ("GMOM", lambda: fetch_etfcom("GMOM")),
    ("RPAR", lambda: fetch_etfcom("RPAR")),
    ("DBMF", lambda: fetch_etfcom("DBMF")),
    ("AOA",  lambda: fetch_etfcom("AOA")),
    ("AOR",  lambda: fetch_etfcom("AOR")),
    ("MAGR", lambda: fetch_investing_playwright("MAGR")),
    ("F701", lambda: fetch_investing_playwright("F701")),
    ("F703", lambda: fetch_investing_playwright("F703")),
]


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*55}")
    print(f"  RAPTOR ETF MONITOR — {TODAY}")
    print(f"  Weekday: {WEEKDAY} (0=Lun … 6=Dom)")
    print(f"{'='*55}\n")

    ok_count  = 0
    err_count = 0

    # ── ETF Holdings ──────────────────────────────────────────────────────────
    for ticker, fetch_fn in ETF_CONFIG:
        folder   = ETF_DIR / ticker
        folder.mkdir(parents=True, exist_ok=True)
        out_path = folder / f"{TODAY}.json"

        if out_path.exists():
            print(f"  → {ticker}: già aggiornato oggi, skip")
            ok_count += 1
            continue

        print(f"\n  → Fetching {ticker}...")
        data = fetch_fn()

        if data and data.get("holdings"):
            prev = load_prev(ticker)
            data["strategic_changes"] = compute_strategic_delta(data, prev)
            save_json(out_path, data)
            ok_count += 1
        else:
            print(f"  ✗ {ticker}: nessun dato recuperato")
            err_count += 1

    # ── CFTC COT — ogni venerdì ───────────────────────────────────────────────
    print(f"\n  → CFTC COT...")
    cftc_path = CFTC_DIR / f"{TODAY}.json"

    if WEEKDAY == 4:  # venerdì
        if cftc_path.exists():
            print("  → CFTC: già aggiornato oggi, skip")
        else:
            cot = fetch_cftc()
            if cot and cot.get("markets"):
                save_json(cftc_path, cot)
                ok_count += 1
            else:
                print("  ✗ CFTC: nessun dato recuperato")
                err_count += 1
    else:
        print("  → CFTC: non è venerdì, skip")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  DONE — OK: {ok_count}  ERRORI: {err_count}")
    print(f"{'='*55}\n")

    if err_count > 0:
        sys.exit(1)  # fa fallire il workflow Actions → notifica email


if __name__ == "__main__":
    main()
