# MONITOR — JPMorgan Strategic Allocation ETF Sprint 1

**Audit date:** 26 November 2026  
**Scope:** JMAC, JMAM, JMAG  
**Status:** Primary issuer identity/benchmark/cost verified. Full portfolio feed and automated ingestion remain pending.

## Official product facts

| Ticker | ISIN | Strategic benchmark mix | Ongoing charge | SFDR | Holdings count (dated snapshot) |
|---|---|---|---:|---|---:|
| JMAC | IE000FASRFS4 | 20% equity / 70% bonds / 10% cash | 0.35% | Article 8 | 15 (29 Sep); 16 (13 Nov) |
| JMAM | IE000TWAN2K7 | 60% equity / 40% bonds | 0.35% | Article 8 | 14 (22 Oct); 15 (13 Nov) |
| JMAG | IE000MVWFDH1 | 80% equity / 20% bonds | 0.35% | Article 8 | 12 (20 Oct) |

**Important:** these benchmark allocations are strategic reference mixes, not guarantees of actual holdings or realized exposures; the funds are actively managed and may deviate.

## Official primary sources

- JMAC: https://am.jpmorgan.com/it/it/asset-management/adv/products/jpm-strategic-allocation-conservative-active-ucits-etf-eur-acc-ie000fasrfs4
- JMAM: https://am.jpmorgan.com/it/it/asset-management/adv/products/jpm-strategic-allocation-moderate-active-ucits-etf-eur-acc-ie000twan2k7
- JMAG: https://am.jpmorgan.com/it/en/asset-management/institutional/products/jpm-strategic-allocation-growth-active-ucits-etf-eur-acc-ie000mvwfdh1
- Official 2026 product list: https://am.jpmorgan.com/content/dam/jpm-am-aem/emea/regional/en/regulatory/product-list/etf-product-list-emea.pdf

## Audit result

- Product identities/ISIN: verified on issuer pages.
- EUR accumulating share class and Ireland domicile: verified.
- SFDR Article 8 and ongoing charge 0.35%: verified.
- Benchmark strategic mix: verified in issuer product list.
- Current holdings counts: issuer product-page snapshots found; counts vary by as-of date and portfolio.
- Full holdings CSV/API endpoint: not identified/validated.
- Parser/normalized weights/reconciliation: not tested.
- Promotion to active monitor: blocked pending official holdings data and reproducible automated retrieval.

## Next
Inspect JPM product-page portfolio/download controls and fund-document APIs; obtain actual holdings file, parse constituents, compare fund exposures to benchmark allocations, then test repeated retrieval and weight reconciliation.
