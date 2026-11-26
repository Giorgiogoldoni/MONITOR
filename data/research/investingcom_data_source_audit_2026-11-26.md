# Investing.com data-source feasibility audit — 2026-11-26

## Objective
Evaluate whether Investing.com can become the primary raw market-data source for MONITOR (daily OHLC, volume, historical series for ETFs and benchmarks).

## Findings
- Investing.com support explicitly says **there is no public API**; provider contracts prevent exposing one. Officially offered alternative is their embeddable widgets.
- Unofficial wrappers (e.g. investpy) depend on site endpoints/scraping and have a history of breaking when the website changes. Automated access/scraping also raises Terms-of-Service concerns.
- Third-party paid services advertise Investing.com-derived datasets/APIs. They are not official Investing.com APIs and add a vendor, cost, reliability and licensing dependency.
- Existing MONITOR return-history workflow currently uses Yahoo Finance's unofficial chart endpoint for a small US proxy universe. It is exploratory and clearly labels adjusted close as not official NAV / not currency-normalized.

## Decision
Do **not** replace the working price-history pipeline with direct Investing.com scraping or undocumented endpoints. Do not call it an official feed or treat downloaded data as exchange-grade.

## Proposed architecture
1. **Provider adapter interface**: standardized rows: symbol/id, instrument mapping, date/time, open, high, low, close, volume, currency, source, fetched_at, adjustment/quality flags.
2. **Source registry**: keep provider + exact instrument link/ID + exchange/currency/share-class mapping + tested status for each instrument. Investing.com link is a human-verification reference, not an automated scraping instruction.
3. **Primary/secondary provider selection**: prefer a licensed API/data vendor with ETF coverage, history, dividends/adjustments, predictable rate limits and permission for automated use. Keep Investing.com as manual cross-check/reference unless access is licensed/approved.
4. **Validation layer**: duplicate dates, gaps, currency, exchange, split/dividend adjustments, stale data, OHLC consistency, outlier/zero volume, and cross-source close-price checks.
5. **Research-only pilot**: test a handful of instruments using a provider with documented API/terms. Compare against Investing.com visible historical values manually for a sample; do not redistribute vendor raw data without rights.

## Status
- Investing.com official public API: **not available**.
- Direct automated fetch from Investing.com: **not approved/implemented**.
- Third-party Investing-derived API/scraper: **not selected**; requires vendor, credentials, price, terms and test.
- MONITOR existing Yahoo exploratory pipeline: **left unchanged**.
- Next decision required before production: choose a permitted licensed provider, or user-supplied exports / manual source checks.
