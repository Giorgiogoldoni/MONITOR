# Multi-asset holdings source audit — 2026-11-25

## Audit status
Phase 1 screening has been started across the expanded research registry. This is a **research-only universe** and not a buy list or active MONITOR holding list.

- Candidate records: **50**
- Provider/issuer groups: **21**
- Duplicate ISINs in the registry: **0**
- Records with missing ticker, ISIN or TER: **5**
- Fully validated download-and-parser feeds: **0** (no source file has yet passed the complete CI integration gate)

## Automated registry checks
The first structural check found the following incomplete identity/cost records:
1. iShares Conservative Portfolio — ticker not recorded.
2. iShares Moderate Portfolio — ticker not recorded.
3. First Trust FactorFX — ISIN and TER not recorded.
4. BNP Global Equity Long/Short — ticker, ISIN and TER not recorded.
5. BNP European Equity Buffer June — ticker not recorded.

Ticker should be treated as exchange-specific. ISIN is the primary identifier, and TER must be tied to the precise share class. The registry has no duplicate ISINs at this stage.

## Category taxonomy
The registry now tags each candidate into a screening category:
- strategic_multi_asset
- efficient_core
- managed_futures_trend
- equity_long_short
- commodity_carry
- options_income
- defined_outcome_buffer
- options_income_etp
- other_alternative

These tags are screening labels, not risk ratings.

## Initial primary-source checks

### VanEck Multi-Asset
Issuer's Italian multi-asset overview confirms the three allocations, ISINs, TERs and AUM as displayed:
- **DTM** NL0009272764: 25% global equities, 35% government bonds, 35% corporate bonds, 5% listed real estate; TER 0.28%; AUM €20.5m (10 Sep 2026).
- **NTM** NL0009272772: 40% equities, 25% government bonds, 25% corporate bonds, 10% listed real estate; TER 0.30%; AUM €42.8m (10 Sep 2026).
- **TOF** NL0009272780: 60% equities, 15% government bonds, 15% corporate bonds, 10% listed real estate; TER 0.32%; AUM €33.5m (10 Sep 2026).
Official issuer source: https://www.vaneck.com/it/it/theme/multi-asset-investing/

**Screening conclusion:** Low-cost and transparent allocations, but modest AUM is a liquidity/closure-monitoring consideration. They are conventional multi-asset exposure, not a unique diversifier. NTM/TOF are the more relevant comparison against balanced/growth portfolios.

### iMGP DBi Managed Futures
Issuer source confirms the R USD UCITS ETF ISIN LU2951555585, 0.75% ongoing charges, daily liquidity, synthetic implementation and managed-futures strategy across liquid futures, with a basket-replication approach. Issuer page: https://www.imgp.com/imgp-dbi-managed-futures-fund/

EUR share class LU2951555403 is also issuer-listed. The registry TER requires a **share-class fee reconciliation**: the issuer page shows management fee 0.55%; ongoing charge figure/TER should be reconciled from the current KID/factsheet before marking final. EUR hedged LU3359622902 has a separate share class and short record.

**Screening conclusion:** One of the most compelling diversifier candidates in the current universe, but not a substitute for equities or bonds. Whipsaw risk, synthetic implementation, futures/roll and strategy replication model must be assessed. Historical crisis performance and rolling correlation should be tested; its ETF record is short.

## Preliminary radar (not a purchase recommendation)
Priority order for the next evidence and quantitative round:

| Priority | Candidate group | Why it merits attention | Main risk / gate |
|---|---|---|---|
| 1 | Managed Futures: BNP FOLOW/EEAU, iMGP DBi, Mandatum MAAF | Potential trend/alternative diversifier; different return driver from static 60/40 | Short ETF histories, strategy/model risk, volatility/whipsaw; fees and liquidity |
| 2 | Active global long-short: BNP SLEEK | Quality/value/momentum/low-volatility systematic long-short design | Short live history, synthetic exposure, net-long bias; confirm full costs |
| 3 | Dynamic multi-asset: ODDO OBBA, JPM strategic allocation, Fineco ACTEQ/ACT60 | Active allocation may adapt to regimes; useful direct comparison to passive baskets | Costs, active risk, holdings transparency, track record |
| 4 | Low-cost strategic multi-asset: VanEck, Xtrackers, Vanguard, iShares, Amundi | Simplicity and low fees; useful benchmark/portfolio alternatives | Equity/bond concentration, rebalancing rules, AUM and product overlap |
| 5 | Buffer / defined outcome: BNP Buffer June | Defined conditional buffer and capped upside can have a specific use-case | Outcome dates, cap, buffer mechanics and path/period dependence |
| 6 | Put-write / option income: UBS BCFS/UBPW | Alternative source of premium income | Equity tail risk; premiums do not eliminate downside |
| 7 | Income ETPs: IncomeShares MLTY/GRWY; preferred income PFFI | High-distribution structures for specialized income use | ETP/wrapper, options exposure, NAV erosion and distribution sustainability |
| 8 | Leveraged commodity carry: UBS UEQC/UEQV | Specialized carry exposure | 2.5x leverage, synthetic and commodity risks; high-risk satellite only |

## Screening scorecard (proposed, before quantitative validation)
Each candidate will be scored 0–5 and weighted:
- Diversification benefit / low correlation: **25%**
- Robustness across market regimes: **20%**
- Risk-adjusted performance / drawdown: **20%**
- Transparency and reproducibility: **15%**
- Costs: **10%**
- Liquidity/AUM/spread: **10%**

No numeric product scores are assigned yet: data and comparable live/strategy histories must first be gathered. Scores will not be fabricated from marketing material.

## Audit backlog
1. Validate the remaining 45 candidates against issuer/KID/factsheet and record source date.
2. Reconcile ISIN, exchange ticker, share class, TER/ongoing charges, AUM, launch date and replication.
3. Flag products with short live histories separately from simulated/strategy histories.
4. Build a comparison dataset with monthly total returns, drawdowns, volatility, correlations and crisis windows; keep backtests clearly separated from live results.
5. Only after the feed and parser tests pass, promote products from research to monitored dashboard status.

## Integration gate
- official source endpoint verified
- download tested in CI/runtime
- source date parsed (not file mtime)
- identifiers and weights normalized
- weight total validated with tolerance
- no stale snapshot appended
- comparison with previous snapshot tested

Manual upload fallback remains until automated source is reliable.
