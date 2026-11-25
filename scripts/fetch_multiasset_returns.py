#!/usr/bin/env python3
"""Download monthly adjusted prices for the MONITOR multi-asset research universe.
Yahoo Finance chart endpoint is unofficial; this is exploratory research, not production data.
"""
import csv, json, math, os, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data/research/returns_universe.json"
OUT = ROOT / "data/research/returns"
HIST = OUT / "monthly_adjusted_prices.csv"
METRICS = OUT / "metrics.json"
SOURCE = "Yahoo Finance chart endpoint (unofficial)"
UA = "Mozilla/5.0 (compatible; MONITOR-research/1.0)"

def fetch(symbol):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(symbol, safe="") + "?range=10y&interval=1mo&events=div%2Csplits"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    chart = data.get("chart", {})
    if chart.get("error") or not chart.get("result"):
        raise RuntimeError(str(chart.get("error") or "empty result"))
    r = chart["result"][0]
    ts = r.get("timestamp", [])
    adj = r.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])
    close = r.get("indicators", {}).get("quote", [{}])[0].get("close", [])
    vals = adj if adj else close
    rows = {}
    for t, v in zip(ts, vals):
        if v is None: continue
        month = datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m")
        rows[month] = round(float(v), 8)
    return rows, r.get("meta", {}).get("currency")

def ret_series(prices):
    months = sorted(prices)
    returns = {}
    for i in range(1, len(months)):
        p0, p1 = prices[months[i-1]], prices[months[i]]
        if p0 and p1: returns[months[i]] = p1/p0-1
    return returns

def calc(prices, ret):
    months=sorted(prices)
    if len(months)<2: return {"observations":len(months),"error":"insufficient data"}
    first,last=prices[months[0]],prices[months[-1]]
    span=(datetime.strptime(months[-1],"%Y-%m")-datetime.strptime(months[0],"%Y-%m")).days/365.25
    vals=list(ret.values())
    avg=sum(vals)/len(vals) if vals else 0
    vol=(sum((x-avg)**2 for x in vals)/(len(vals)-1))**.5*math.sqrt(12) if len(vals)>1 else None
    equity=peak=1.0; maxdd=0
    for x in vals:
        equity*=1+x; peak=max(peak,equity); maxdd=min(maxdd,equity/peak-1)
    cagr=(last/first)**(1/span)-1 if span>0 and first>0 else None
    sharpe=(avg*12)/(vol) if vol and vol>0 else None
    return {"observations_monthly":len(vals),"start_month":months[0],"end_month":months[-1],
            "cumulative_return_adj_close":last/first-1,"cagr_adj_close":cagr,
            "annualized_volatility":vol,"max_drawdown_monthly":maxdd,"sharpe_rf0_approx":sharpe}

def correlation(a,b):
    common=sorted(set(a)&set(b))
    if len(common)<12:return {"n":len(common),"correlation":None}
    x=[a[m] for m in common]; y=[b[m] for m in common]
    mx=sum(x)/len(x); my=sum(y)/len(y)
    num=sum((u-mx)*(v-my) for u,v in zip(x,y))
    dx=sum((u-mx)**2 for u in x); dy=sum((v-my)**2 for v in y)
    return {"n":len(common),"correlation":num/math.sqrt(dx*dy) if dx*dy else None}

def main():
    universe=json.loads(CONFIG.read_text())
    allp={}; metadata={}; errors={}
    for item in universe["instruments"]:
        sym=item["yahoo_symbol"]
        try:
            prices,currency=fetch(sym); allp[item["id"]]=prices
            metadata[item["id"]]={**item,"currency_return_series":currency,"source":SOURCE,"status":"ok","observations":len(prices)}
            print(f"OK {sym}: {len(prices)} monthly bars")
        except Exception as e:
            errors[item["id"]]=str(e); metadata[item["id"]]={**item,"source":SOURCE,"status":"error","error":str(e)}
            print(f"ERROR {sym}: {e}")
    OUT.mkdir(parents=True,exist_ok=True)
    months=sorted({m for p in allp.values() for m in p})
    with HIST.open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["month"]+[i["id"] for i in universe["instruments"]])
        for m in months: w.writerow([m]+[allp.get(i["id"],{}).get(m,"") for i in universe["instruments"]])
    returns={k:ret_series(v) for k,v in allp.items()}
    benchmarks=universe.get("benchmark_ids",[])
    results={}
    for k,p in allp.items():
        results[k]={"instrument":metadata[k],"metrics":calc(p,returns[k]),"correlations":{}}
        for b in benchmarks:
            if b in returns and b!=k: results[k]["correlations"][b]=correlation(returns[k],returns[b])
    payload={"generated_utc":datetime.now(timezone.utc).isoformat(),"source":SOURCE,
             "source_warning":"Unofficial Yahoo chart interface; adjusted close is a proxy for dividend/split-adjusted total return. Not official NAV, not currency-normalized, and not guaranteed complete.",
             "results":results,"errors":errors}
    METRICS.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n")
    print(f"Wrote {HIST} and {METRICS}; errors={len(errors)}")
    if errors: raise SystemExit(1)

if __name__=="__main__": main()
