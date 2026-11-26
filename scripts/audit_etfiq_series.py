#!/usr/bin/env python3
"""ETFIQ series endpoint availability pilot for MONITOR ETF universe."""
import json, urllib.request, urllib.error, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = json.loads((ROOT / "data/index.json").read_text(encoding="utf-8"))
TICKERS = sorted(INDEX.get("etfs", {}).keys())
URL = "https://etfiq.com/data/series/{ticker}.json"
rows=[]
for ticker in TICKERS:
    url=URL.format(ticker=ticker.lower())
    row={"ticker":ticker,"url":url,"status":"unknown"}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"MONITOR-ETFIQ-pilot/1.0"})
        with urllib.request.urlopen(req,timeout=20) as r:
            payload=json.loads(r.read().decode("utf-8"))
            row["http_status"]=r.status
            row["keys"]=list(payload.keys())[:15]
            row["as_of"]=payload.get("cite",{}).get("as_of") or payload.get("asOf")
            row["status"]="available"
            # tolerate schema variation, report rather than assume
            data=payload.get("data") or payload.get("series") or payload.get("prices")
            if isinstance(data,list):
                row["records"]=len(data)
                row["first"]=data[0] if data else None
                row["last"]=data[-1] if data else None
            elif isinstance(payload.get("dates"),list):
                row["records"]=len(payload["dates"])
                row["first_date"]=payload["dates"][0] if payload["dates"] else None
                row["last_date"]=payload["dates"][-1] if payload["dates"] else None
            row["schema_note"]="Inspect fields; not yet certified for production use."
    except urllib.error.HTTPError as e:
        row["status"]="http_error"; row["http_status"]=e.code
    except Exception as e:
        row["status"]="error"; row["error"]=str(e)[:240]
    rows.append(row)

asof=datetime.datetime.now(datetime.timezone.utc).isoformat()
result={"checked_at_utc":asof,"source":"ETFIQ open series endpoint","source_url":"https://etfiq.com/data/","ticker_count":len(TICKERS),"available":sum(x["status"]=="available" for x in rows),"rows":rows}
out=ROOT/"data/research/etfiq_series_pilot.json"
out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({k:result[k] for k in ("checked_at_utc","ticker_count","available")},indent=2))
for row in rows: print(row["ticker"],row["status"],row.get("http_status",""),row.get("records",""),row.get("as_of",""),row.get("error",""))
