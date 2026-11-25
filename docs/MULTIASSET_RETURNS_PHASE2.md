# Phase 2 — Historical return diagnostics

## First controlled data collection
The starter universe is intentionally small and consists of **US-listed comparators/proxies** (DBMF, RPAR, AOA, AOR, VT, BND). It is not yet a representative set of the 50 EU candidates. In particular, DBMF_US is not the same share class/market history as the European UCITS candidate.

## Pipeline
- Script: `scripts/fetch_multiasset_returns.py`
- Universe mapping: `data/research/returns_universe.json`
- Output: `data/research/returns/monthly_adjusted_prices.csv` and `metrics.json`
- GitHub Actions: manual dispatch or monthly schedule.

Uses Yahoo Finance's chart interface (unofficial) with monthly adjusted-close series. The adjusted close is used as a dividend/split-adjusted return proxy. This is not official NAV, may have missing observations, can be blocked/changed, and must not be treated as a licensed production feed.

## Calculations
- Cumulative adjusted-price return and CAGR (where dates allow)
- Annualized monthly volatility
- Maximum drawdown using monthly observations
- Approximate Sharpe ratio with zero risk-free rate
- Monthly return correlations to VT (global equities) and AOR (balanced benchmark)

No FX normalization: series remain in their quote currencies. Metrics are provisional; monthly drawdown underestimates intra-month drawdown. Correlation is shown only with at least 12 overlapping monthly observations. A short history is not extrapolated.

## Gate to expand the universe
Before inclusion of any UCITS candidate: confirm ticker/exchange and ISIN/share class, check adjusted-price coverage, currency and distributions, compare data against official NAV/factsheet, record missing/stale bars, and keep live share-class history distinct from proxy/backtest history. The scorecard remains unscored until enough comparable data and source verification exist.
