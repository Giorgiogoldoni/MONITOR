# Multi-asset holdings source audit — 2026-11-25

## Scope
Candidate research for VanEck DTM/NTM/TOF and JPMorgan JMAC/JMAM/JMAG. These are **not yet active holdings feeds** in MONITOR.

## VanEck
Official product pages publish full holdings tables and a “Download All Holdings” option. DTM page search evidence showed 244 holdings dated 10 Sep 2026. Other official factsheets confirm holdings and product details, but the actual download endpoint/file has not yet been acquired and parser-tested.
- DTM — NL0009272764 — 25% equities, 35% government bonds, 35% corporate bonds, 5% listed real estate — TER 0.28%.
- NTM — NL0009272772 — 40% equities, 25% government bonds, 25% corporate bonds, 10% listed real estate — TER 0.30%.
- TOF — NL0009272780 — 60% equities, 15% government bonds, 15% corporate bonds, 10% listed real estate — TER 0.32%.
Source: [VanEck official multi-asset overview](https://www.vaneck.com/it/it/theme/multi-asset-investing/).

## JPMorgan
Official product portal confirms product pages and holding counts, but a reliable EU UCITS full-holdings download/API was not validated. Do not reuse the US ETF endpoint without evidence.
- JMAC — IE000FASRFS4 — conservative benchmark mix 20/70/10 (equity/bonds/cash), TER 0.35%.
- JMAM — IE000TWAN2K7 — moderate benchmark 60/40, TER 0.35%.
- JMAG — IE000MVWFDH1 — growth benchmark 80/20, TER 0.35%.
Source: [JPMorgan ETF portal](https://am.jpmorgan.com/it/en/asset-management/institutional/products/fund-explorer/etf).

## Integration decision
- Added as research candidates only; not included in active ticker list or index.
- Next gate: acquire official files, test HTTP/format/parser in workflow, parse true holdings date, normalize identifiers and weights, and validate totals/duplicates/staleness.
- Manual upload fallback should remain until automated source is reliable.


## Expanded universe — 2026-11-25

The candidate registry has been broadened beyond strategic allocation products. The groups below are tracked separately to avoid treating alternative strategies or specialist income funds as equivalent to a conventional balanced portfolio.

### ODDO BHF Global Balanced Allocation
- OBBA — IE000V0Q8BV4 — TER 0.30%: active dynamic multi-asset ETF using UCITS ETFs and ETCs; equity and fixed-income exposures can each vary broadly; commodities capped at 10%.
- OBAA — IE000UXI85C0 — TER 1.10%: separate AAA share class, identified as a separate record; fee difference is material and requires class-specific verification.
- Official issuer/HANetf product page: https://hanetf.com/it/fund/oddo-bhf-global-balanced-allocation-active-ucits-etf/.

### Man Active Trend Enhanced
- MATE — IE000BS31R00 — TER 0.95% (Borsa Italiana reports 0.95%): global developed-market equity exposure combined with trend-following overlay across futures/forwards in equities, fixed income, commodities and currencies. Classified as **trend-following diversifier**, not a conventional fixed allocation ETF.
- Product listing and issuer description: https://www.borsaitaliana.it/borsa/etf/scheda/IE000BS31R00-ETFP.html.

### BNP Paribas Easy Managed Futures
- ISIN LU3307218399. Official KID identifies a UCITS ETF. Ticker, fee, holdings download and source endpoint remain unverified. Track in managed-futures/alternative-diversifier category, not core allocation.
- Official KID reference: https://docfinder.bnpparibas-am.com/api/files/ebdb5076-fc74-4d15-8db2-c5fa3b63e7fc/512.

### HANetf Infrastructure Capital Preferred Income
- PFFI — IE0008LRGGP4 — TER 0.80%. Specialist actively managed preferred/hybrid income strategy, monthly distribution, not a broad multi-asset allocation ETF. Included only in adjacent income-diversifier research.
- Official product page: https://hanetf.com/it/fund/infrastructure-capital-preferred-income-ucits-etf-dist/.

## Cautions
- Candidate universe is not an endorsement or buy list.
- Tickers can vary by exchange/share class; ISIN is the primary identity key.
- Where share classes have materially different fees, preserve separate records.
- Do not compare specialist income or managed-futures strategies directly with traditional 20/40/60/80 allocation ETFs without distinct risk labels.
- Dashboard counts should be interpreted as research records, not a validated count of all market products.
