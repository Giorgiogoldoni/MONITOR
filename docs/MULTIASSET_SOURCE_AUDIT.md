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
