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
- specialist_income
- currency_carry
- sector_multi_asset
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


## Phase 1B — qualitative triage of all 50 candidates

This pass is a **qualitative prioritization only**. It does not assign performance, Sharpe, volatility, drawdown or correlation scores: a comparable monthly total-return dataset has not yet been assembled. Labels do not mean the product has passed the issuer/KID verification gate.

### Priority due diligence (10)
- BNP Managed Futures FOLOW/EEAU
- iMGP DBi Managed Futures DBMF
- iMGP DBi Managed Futures ex-Commodities
- BNP Global Equity Long/Short SLEEK
- ODDO BHF Global Balanced Allocation C (OBBA)
- ODDO BHF Global Balanced Allocation AAA (OBAA)
- Fineco Active Portfolios 60% (ACT60)
- WisdomTree Global Efficient Core (GEC)
- WisdomTree US Efficient Core (UEC)
- WisdomTree Eurozone Efficient Core (ZEC)

**Why:** strategy differentiation, diversifier potential, or transparent leverage-efficient exposure. The selection is for research—not endorsement or buy signals.

### Benchmark controls (5)
- VanEck Multi-Asset Balanced (NTM)
- JPM Strategic Allocation Moderate (JMAM)
- Vanguard LifeStrategy 60 (VLS60)
- Xtrackers Diversified Portfolio 60 (XEQ6)
- iShares Growth Portfolio (MAGR)

Use these as conventional multi-asset comparison controls. They help determine whether a more complex strategy actually improves on a simple balanced portfolio.

### Specialized watchlist (9)
- Mandatum MAAF — high TER / short history and model complexity
- UBS UEQC/UEQV — 2.5x commodity carry leverage
- UBS BCFS/UBPW — put-write premium exposure, equity downside remains
- BNP Buffer June — period-specific buffer, upside cap and outcome mechanics
- IncomeShares MLTY/MLAY and GRWY/MSTY — options income ETP structure; distributions are not total return
- HANetf PFFI — specialist preferred-income exposure

### Hold / identity or relevance gate (5)
- First Trust FactorFX — missing ISIN and TER in registry
- SPDR MAGI — infrastructure allocation; not directly comparable to diversified multi-asset
- iShares Conservative and Moderate — missing exchange ticker in registry; ISIN still primary key
- Goshawk — require current factsheet, liquidity/AUM and strategy review before priority

The other 21 candidates remain standard due diligence; they are neither rejected nor shortlisted.

### Scorecard for the next phase (weights)
| Factor | Weight |
|---|---:|
| Diversification benefit / correlation | 25% |
| Regime robustness | 20% |
| Risk-adjusted return and drawdown | 20% |
| Transparency / reproducibility | 15% |
| Costs | 10% |
| Liquidity, AUM and spread | 10% |

Do not calculate final scores until data is comparable and sources are documented. Live track records and simulated/strategy histories must be kept separate.

### Phase 2 data requirements
For every shortlisted fund: monthly total returns, inception date, NAV vs market price, AUM, bid-ask spread if available, benchmark, holdings/strategy disclosure, fee and share-class KID; then calculate rolling 12/36-month volatility, max drawdown, Sharpe/Sortino (with stated assumptions), correlations against global equity, aggregate bonds and conventional 60/40, and stress windows. Where history is short, report N/A rather than extrapolate.
