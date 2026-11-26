# MONITOR — ETF Holdings Research Sprint 1: VanEck update

**Audit date:** 2026-11-26  
**Scope:** DTM, NTM, TOF — issuer primary sources  
**Status:** source evidence upgraded; automated holdings download/parser remains pending. These ETFs are NOT promoted to active monitor.

## Confirmed issuer data

| Ticker | ISIN | Strategic allocation | TER | Latest evidence |
|---|---|---|---:|---|
| DTM | NL0009272764 | 35% govt bonds / 35% corporate bonds / 25% global equities / 5% REITs | 0.28% | Official factsheet dated 2026-10-31; official product page updated 2026-11-20 |
| NTM | NL0009272772 | 25% govt bonds / 25% corporate bonds / 40% global equities / 10% REITs | 0.30% | Official factsheet dated 2026-10-31 |
| TOF | NL0009272780 | 15% govt bonds / 15% corporate bonds / 60% global equities / 10% REITs | 0.32% | Official factsheet dated 2026-10-31; issuer holdings table visible on product page |

## Latest official factsheet top-10 snapshot

**DTM — 31 Oct 2026**
- Germany government bond 4.69%
- Anheuser-Busch InBev 2.93%
- France OAT 2.52%
- Spain government bond 2.42%
- Alphabet 1.88%
- Belgium government bond 1.80%
- France OAT 1.64%
- Spain government bond 1.61%
- Italy BTP 1.53%
- Italy BTP 1.52%
- Top 10 subtotal 22.54%; remaining holdings 77.04%; other/cash 0.42%

**NTM — 31 Oct 2026**
- Italy BTP 2.41%
- Anheuser-Busch InBev 1.62%
- Welltower 1.49%
- Spain government bond 1.44%
- Belgium government bond 1.31%
- Germany government bond 1.29%
- Italy BTP 1.27%
- Prologis 1.19%
- Deutsche Bahn 1.16%
- HSBC 1.14%
- Top 10 subtotal 14.31%; remaining holdings 85.44%; other/cash 0.25%

**TOF — 31 Oct 2026**
- Germany government bond 2.09%
- Welltower 1.79%
- Prologis 1.35%
- France OAT 1.17%
- Germany government bond 1.14%
- Italy BTP 0.99%
- Belgium government bond 0.91%
- Realty Income 0.87%
- Simon Property Group 0.83%
- Spain government bond 0.79%
- Top 10 subtotal 11.94%; remaining holdings 87.41%; other/cash 0.66%

## Official source links

- VanEck multi-asset overview / strategic weights: https://www.vaneck.com/it/it/theme/multi-asset-investing/
- DTM factsheet (Oct 2026): https://www.vaneck.com/it/it/library/fact-sheets/dtm-fact-sheet.pdf
- NTM factsheet (Oct 2026): https://www.vaneck.com/pt/en/library/fact-sheets/ntm-fact-sheet.pdf
- TOF factsheet (Oct 2026): https://www.vaneck.com/it/en/library/fact-sheets/tof-fact-sheet.pdf
- TOF product page holdings table: https://www.vaneck.com/ro/en/investments/growth-multi-asset-etf

## Audit result and next technical gate

- **Issuer evidence:** verified, primary sources.
- **Factsheet snapshot:** verified as dated 31 Oct 2026 (top 10 only).
- **Full holdings table/download:** issuer pages show holdings and download controls, but direct URL capture and machine-readable download validation are not yet complete.
- **Parser / data normalization:** not tested.
- **Promotion to active monitor:** blocked until file download, schema validation, weight reconciliation (including cash/derivatives), and repeatable automated fetch pass.

Do not treat factsheet top-10 as complete portfolio holdings.
