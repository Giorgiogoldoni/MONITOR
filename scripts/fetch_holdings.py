#!/usr/bin/env python3
"""
RAPTOR ETF MONITOR — Holdings & CFTC Fetcher v4
═══════════════════════════════════════════════════════
ETF (tutti)  → CSV manuali in data/manual/TICKER.csv
               Formato investing.com: Nome,Simbolo,% Peso,...
               La data nel JSON = data del file CSV (mtime) o TODAY

CFTC COT     → CFTC.gov automatico, sempre
               File salvato con la data interna del report (martedì)
               Non dipende dal giorno in cui gira il workflow
═══════════════════════════════════════════════════════
PROCEDURA SETTIMANALE (5 min):
  1. Vai su investing.com, scarica il CSV per ogni ETF
  2. Rinomina il file: GMOM.csv, RPAR.csv, ... (maiuscolo)
  3. Carica in data/manual/ nel repo
  4. Esegui il workflow (o aspetta lunedì)
"""

import json
import sys
import datetime
import csv
import io
from pathlib import Path

import requests

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE     = Path(__file__).parent.parent
DATA     = BASE / "data"
ETF_DIR  = DATA / "holdings"
CFTC_DIR = DATA / "cftc"
MANUAL   = DATA / "manual"

for d in [ETF_DIR, CFTC_DIR, MANUAL]:
    d.mkdir(parents=True, exist_ok=True)

TODAY   = datetime.date.today().isoformat()
WEEKDAY = datetime.date.today().weekday()

ETFS = ["GMOM", "RPAR", "DBMF", "AOA", "AOR", "MAGR", "F701", "F703"]

# ── HTTP ───────────────────────────────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; RAPTOR-ETF-Monitor/4.0)",
    "Accept":     "text/plain,text/csv,*/*",
})


def get(url, timeout=60):
    return SESSION.get(url, timeout=timeout)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ salvato {path.relative_to(BASE)}")


def load_prev(etf):
    folder = ETF_DIR / etf
    if not folder.exists():
        return None
    files = sorted(folder.glob("*.json"))
    return json.loads(files[-1].read_text(encoding="utf-8")) if files else None


def parse_weight(s):
    """Converte '14,39%' o '14.39%' o '14.39' in float."""
    try:
        return round(float(str(s).replace("%", "").replace(",", ".").strip()), 4)
    except Exception:
        return 0.0


# ── Parser CSV investing.com ───────────────────────────────────────────────────
# Formato: Nome,Simbolo,% Peso,Rialzo,Prezzo,Var. %,Azioni
# (con BOM UTF-8 e virgola come separatore decimale)

def parse_investing_csv(text):
    """
    Parsa il CSV di investing.com.
    Restituisce lista di {name, ticker, weight}.
    """
    text = text.lstrip("\ufeff")  # rimuovi BOM
    reader = csv.DictReader(io.StringIO(text))
    holdings = []
    for row in reader:
        # Cerca colonna nome (può essere "Nome" o "Name")
        name = (
            row.get("Nome") or row.get("Name") or
            row.get("nome") or ""
        ).strip().strip('"')

        # Cerca colonna ticker (può essere "Simbolo" o "Symbol")
        ticker = (
            row.get("Simbolo") or row.get("Symbol") or
            row.get("simbolo") or ""
        ).strip().strip('"')

        # Cerca colonna peso (può essere "% Peso" o "Weight (%)" ecc.)
        weight_raw = (
            row.get("% Peso") or row.get("Weight (%)") or
            row.get("Peso") or row.get("Weight") or "0"
        )
        weight = parse_weight(weight_raw)

        if name and weight > 0:
            holdings.append({"name": name, "ticker": ticker, "weight": weight})

    return holdings


# ── Lettura CSV manuali ────────────────────────────────────────────────────────

def fetch_manual(ticker):
    """
    Legge data/manual/TICKER.csv e lo converte in snapshot JSON.
    La data dello snapshot = data di modifica del file (quando l'hai scaricato).
    """
    csv_path = MANUAL / f"{ticker}.csv"
    if not csv_path.exists():
        print(f"    ✗ file non trovato: {csv_path.relative_to(BASE)}")
        return None

    # Data snapshot = data ultima modifica del file CSV
    mtime = datetime.date.fromtimestamp(csv_path.stat().st_mtime).isoformat()

    text = csv_path.read_text(encoding="utf-8-sig")  # utf-8-sig gestisce BOM
    holdings = parse_investing_csv(text)

    if not holdings:
        print(f"    ✗ nessuna holding nel CSV di {ticker}")
        return None

    print(f"    → {len(holdings)} holdings da CSV manuale (data file: {mtime})")
    return {
        "date":     mtime,
        "source":   "manual/investing.com",
        "holdings": holdings,
    }


# ── Strategic delta ────────────────────────────────────────────────────────────

def compute_strategic_delta(current, prev):
    if not prev:
        return []

    def key(h):
        return (h.get("ticker") or h.get("name", "")).strip()

    prev_map = {key(h): h["weight"] for h in prev.get("holdings", []) if key(h)}
    deltas = []
    for h in current.get("holdings", []):
        k = key(h)
        if not k:
            continue
        prev_w = prev_map.get(k, 0.0)
        delta  = round(h["weight"] - prev_w, 4)
        if abs(delta) >= 1.5:
            deltas.append({
                "ticker":      h.get("ticker", ""),
                "name":        h.get("name", k),
                "prev_weight": round(prev_w, 4),
                "curr_weight": round(h["weight"], 4),
                "delta":       delta,
                "direction":   "▲ AUMENTO" if delta > 0 else "▼ RIDUZIONE",
            })
    return sorted(deltas, key=lambda x: abs(x["delta"]), reverse=True)


# ── CFTC COT — automatico, sempre ─────────────────────────────────────────────
# URL corretta: file TXT diretto (non ZIP)
# URL corretta: file TXT diretto (non ZIP)
CFTC_URL_FUT = "https://www.cftc.gov/dea/newcot/FinFutWk.txt"   # Futures only
CFTC_URL_COM = "https://www.cftc.gov/dea/newcot/FinComWk.txt"   # Futures + Options

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
    """
    Converte la data CFTC (formato YYMMDD o YYYY-MM-DD) in ISO YYYY-MM-DD.
    Es: '260513' → '2026-05-13'
    """
    raw = str(raw).strip()
    if len(raw) == 6 and raw.isdigit():
        # YYMMDD
        yy, mm, dd = raw[:2], raw[2:4], raw[4:6]
        year = int("20" + yy)
        return f"{year}-{mm}-{dd}"
    if len(raw) == 10 and "-" in raw:
        return raw  # già ISO
    return TODAY  # fallback


def fetch_cftc_file(url):
    """
    Scarica un file TFF CFTC (Futures Only o Futures+Options).
    Restituisce (data, dict risultati) o (None, None) in caso di errore.
    """
    print(f"    GET {url}")
    try:
        r = get(url)
        r.raise_for_status()
        text = r.text.lstrip("\ufeff")

        reader = csv.reader(io.StringIO(text))
        results = {}
        report_date = None

        def to_int(s):
            try: return int(str(s).replace(",","").strip())
            except: return 0

        for cols in reader:
            if len(cols) < 17:
                continue
            market_name = cols[0].strip().strip('"')
            cftc_code   = cols[3].strip().strip('"')
            if report_date is None:
                report_date = parse_cftc_date(cols[1].strip())
            for label, code in COT_MARKETS.items():
                if label in results:
                    continue
                if code_matches(cftc_code, code) or code in market_name:
                    try:
                        ll  = to_int(cols[15])
                        ls  = to_int(cols[16])
                        al  = to_int(cols[12])
                        as_ = to_int(cols[13])
                        results[label] = {
                            "market":      market_name,
                            "report_date": report_date or TODAY,
                            "lev_long":    ll,
                            "lev_short":   ls,
                            "lev_net":     ll - ls,
                            "asset_long":  al,
                            "asset_short": as_,
                        }
                    except Exception as ex:
                        print(f"    ⚠ parse '{label}': {ex}")

        if not results:
            print("    ✗ nessun mercato trovato")
            return None, None

        print(f"    → {len(results)}/{len(COT_MARKETS)} mercati · data: {report_date}")
        return report_date, results

    except Exception as e:
        print(f"    ✗ {e}")
        return None, None


def fetch_cftc():
    """
    Scarica TFF Futures Only + Futures+Options Combined.
    Salva due file:
      data/cftc/YYYY-MM-DD.json          (futures only)
      data/cftc/YYYY-MM-DD_combined.json (futures + options)
    """
    report_date_f, results_f = fetch_cftc_file(CFTC_URL_FUT)
    report_date_c, results_c = fetch_cftc_file(CFTC_URL_COM)

    report_date = report_date_f or report_date_c
    if not report_date:
        return None, None

    # Merge: futures only come base, combined come campo aggiuntivo
    merged = {}
    all_labels = set(list(results_f.keys()) + list(results_c.keys()))
    for label in all_labels:
        base = results_f.get(label) or results_c.get(label)
        combined = results_c.get(label)
        if base:
            entry = dict(base)
            if combined:
                entry["lev_long_com"]  = combined["lev_long"]
                entry["lev_short_com"] = combined["lev_short"]
                entry["lev_net_com"]   = combined["lev_net"]
            merged[label] = entry

    if not merged:
        return None, None

    return {"date": report_date, "source": CFTC_URL_FUT, "markets": merged}, report_date


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*55}")
    print(f"  RAPTOR ETF MONITOR v4 — {TODAY}")
    print(f"  Weekday: {WEEKDAY} (0=Lun … 6=Dom)")
    print(f"{'='*55}\n")

    ok_count = err_count = skip_count = 0

    # ── ETF Holdings da CSV manuali ───────────────────────────────────────────
    print("  ── ETF HOLDINGS (CSV manuali) ──\n")
    for ticker in ETFS:
        (ETF_DIR / ticker).mkdir(parents=True, exist_ok=True)
        csv_path = MANUAL / f"{ticker}.csv"

        if not csv_path.exists():
            print(f"  → {ticker}: ⚠ CSV non trovato in data/manual/{ticker}.csv — skip")
            skip_count += 1
            continue

        print(f"  → {ticker}...")
        data = fetch_manual(ticker)

        if not data or not data.get("holdings"):
            print(f"  ✗ {ticker}: nessun dato estratto dal CSV")
            err_count += 1
            continue

        # Usa la data del file come nome snapshot
        snap_date = data["date"]
        out_path  = ETF_DIR / ticker / f"{snap_date}.json"

        if out_path.exists():
            print(f"  → {ticker}: snapshot {snap_date} già presente, skip")
            skip_count += 1
            continue

        data["strategic_changes"] = compute_strategic_delta(data, load_prev(ticker))
        save_json(out_path, data)
        ok_count += 1

    # ── CFTC — sempre, usa data interna del report ────────────────────────────
    print(f"\n  ── CFTC COT (automatico) ──\n  → Fetching...")
    cot, report_date = fetch_cftc()

    if cot and report_date:
        cftc_path = CFTC_DIR / f"{report_date}.json"
        if cftc_path.exists():
            print(f"  → CFTC: report {report_date} già presente, skip")
            skip_count += 1
        else:
            save_json(cftc_path, cot)
            ok_count += 1
    else:
        print("  ✗ CFTC: nessun dato recuperato")
        err_count += 1

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  DONE — OK: {ok_count}  SKIP: {skip_count}  ERRORI: {err_count}")
    print(f"{'='*55}\n")

    # Esce con errore solo se tutti gli ETF sono mancanti (nessun CSV caricato)
    # Non blocca se alcuni ETF mancano — il CFTC deve sempre girare
    if err_count > 0 and ok_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
