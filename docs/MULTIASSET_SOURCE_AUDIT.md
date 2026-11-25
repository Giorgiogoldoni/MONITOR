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


## New managed-futures and liquid alternatives — verified 25 Nov 2026

### BNP Paribas Easy Managed Futures
- FOLOW (Euronext/SIX) / EEAU (Xetra), ISIN LU3307218399, TER 0.60%, launched 29 May 2026. Active model-based trend strategy using futures/forwards across equities, fixed income, currencies and commodities; volatility target described as 10–15%. The strategy is synthetically implemented. Verify exchange-specific ticker before trade.
- Source: BNP Paribas issuer strategy overview https://www.bnpparibas-am.com/en-gb/portfolio-perspectives/innovating-with-liquid-alternative-and-buffer-etfs/; ETF profile https://www.justetf.com/en-fr/etf-profile.html?isin=LU3307218399.

### Mandatum Managed Futures
- MAAF — IE000N4P5QK5 — TER 1.70%, listed Xetra 25 Nov 2026. Daily dynamically allocated strategy combining trend-following, mean-reversion, carry and seasonal drivers across global equity, rates, bonds and currency markets. New ETF wrapper: no ETF-specific live track record yet. Official issuer: https://www.mandatum.fi/en/corporation-news/2026/mandatum-brings-its-multi-strategy-managed-futures-approach-to-an-etf/.

### iMGP DBi Managed Futures ETF family
- DBMF — LU2951555585 — 0.75%, actively replicates pre-fee performance of a representative basket of leading CTA/managed-futures funds.
- DBMF / MFA8 (exchange-dependent ticker) — LU3024069877 — 0.75%, managed futures ex-commodities. Distinct exposure design; confirm exchange symbol on broker.
- Official issuer pages: https://www.imgp.com/imgp-dbi-managed-futures-fund/ and https://www.imgp.com/en/fund/LU3024069877-imgp-dbi-managed-futures-ex-commodities-fund-r-usd-ucits-etf/.

### Adjacent strategy candidates
- BNP Paribas Easy Global Equity Long Short UCITS ETF: issuer confirms as part of its liquid alternatives ETF range, but identifier, listing and TER not yet verified; kept as an incomplete research record.
- First Trust FactorFX UCITS ETF: currency carry strategy, adjacent diversifier rather than conventional multi-asset allocation; identity/fees to verify.

## Research priority judgement
1. BNP FOLOW: lower fee than Mandatum and already has a short live record; inspect risk-targeting, exposure report and AUM/liquidity.
2. iMGP DBMF and ex-commodities: transparent strategy description and UCITS ETF share classes; compare replication basket methodology and commodity exposure.
3. Mandatum MAAF: interesting multi-strategy differentiator, but 1.70% fee and brand-new ETF listing make it watch-only pending data and trading history.
4. Keep these separate from core strategic allocation products; no automatic inclusion in portfolios.


## Additional liquid alternative candidates — 25 Nov 2026

### UBS commodity carry
- UEQC — IE00BKFB6L02 — USD accumulating — TER 0.34%; UEQV — IE00BMC5DV85 — EUR hedged — TER 0.34%. Both are synthetic swap-based exposure to a **2.5x leveraged** commodity carry index excluding precious metals. Do not classify as low-risk diversifier; leverage, commodity roll/carry and synthetic counterparty risks apply. Sources: https://www.justetf.com/en-lu/etf-profile.html?isin=IE00BKFB6L02 and https://live.deutsche-boerse.com/en/etf/ubs-cmci-commodity-carry-sf-ucits-etf-heur-acc?mic=XETR.

### UBS Defensive Put Write
- BCFS — IE000V73IL86 — EUR hedged — TER 0.24%; USD share class IE00BLDGHF56 — TER 0.24%. Synthetic strategy selling S&P 500 puts with Treasury/cash component. It can earn option premium but remains exposed to equity downside and gap risk; not a true capital-protection ETF. Sources: https://www.justetf.com/en-it/etf-profile.html?isin=IE000V73IL86 and UBS factsheet https://www.swissfunddata.ch/sfdpub/docs/fsm-8514_25_01-20260131-fr.pdf.

### BNP European Equity Buffer June
- LU3307215619 — TER 0.55%, launched 21 May 2026. Defined-outcome strategy on EURO STOXX 50 with stated 15% buffer over outcome period and capped upside. Buffer is period-specific, not a guarantee; full cap, observation dates and payoff details must be checked before use. Sources: https://www.bnpparibas-am.com/it-it/fundsheet/equity/bnp-paribas-easy-european-equity-buffer-june-ucits-etf-c-lu3307215619 and https://www.justetf.com/en-lu/etf-profile.html?isin=LU3307215619.

### iMGP DBi EUR share classes
- DBMFE — LU2951555403 — EUR share class, TER 0.75% (Borsa Italiana listing confirmed).
- MFEH — LU3359622902 — EUR hedged share class, TER 0.75% (Borsa Italiana listing confirmed).
- Keep these as separate share-class records from the USD DBMF record. Sources: https://www.borsaitaliana.it/borsa/etf/scheda/LU2951555403-XPAR.html and https://www.borsaitaliana.it/borsa/etf/scheda/LU3359622902-XPAR.html.

## Risk taxonomy additions
- **Managed futures / CTA:** potential crisis and trend diversification; can suffer whipsaw and prolonged flat periods.
- **Put-write:** option-premium income with equity crash/gap exposure; no guaranteed floor.
- **Buffer / defined outcome:** conditional downside buffer paired with capped upside, reset/outcome-period dependency.
- **Leveraged commodity carry:** 2.5x exposure and synthetic implementation; treat as high-risk satellite, not strategic multiasset substitute.
