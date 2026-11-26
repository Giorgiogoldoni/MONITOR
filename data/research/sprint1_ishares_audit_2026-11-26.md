# MONITOR — iShares/BlackRock Multi-Asset Sprint 1 audit

**Audit date:** 26 November 2026  
**Scope:** MACV, MODR, MAGR  
**Status:** Issuer identity and downloadable CSV control verified for MACV/MODR. Direct CSV endpoint capture, download validation, parser and full holdings reconciliation are pending. Not promoted into active monitor.

## MACV — Conservative Portfolio
- ISIN: IE00BLP53M98
- TER: 0.25%; EUR accumulating; Ireland UCITS; SFDR Article 8.
- Official issuer page on 23 Nov 2026: share-class assets EUR 16.53m; fund assets EUR 20.20m; holdings count 21.
- Official issuer page exposes “Download latest fund holdings CSV data”; product page says detailed holdings include tickers, names, sectors, market values and weights.
- Latest October factsheet confirms active multi-asset portfolio, at least 80% ESG-screened ETF exposure, conservative risk target.
- Primary URL: https://www.ishares.com/uk/individual/en/products/313196/ishares-conservative-portfolio-ucits-etf-macv
- Factsheet: https://www.ishares.com/gls-download/literature/fact-sheet/macv-ishares-conservative-portfolio-ucits-etf-fund-fact-sheet-en-gb.pdf

## MODR — Moderate Portfolio
- ISIN: IE00BLLZQS08
- TER: 0.25%; EUR accumulating; Ireland UCITS; SFDR Article 8.
- Official issuer page as of 18 Nov 2026: share-class assets EUR 47.68m; fund assets EUR 86.51m; holdings count 20 (17 Nov).
- Official page has detailed holdings analytics and CSV download control.
- Latest factsheet asset allocation (snapshot varies by locale/date): Fixed Income ~52.45–55.27%, Equity ~42.49–44.68%, Alternatives ~2.77–2.94%, Cash/derivatives roughly -0.70 to +0.11%. Use the underlying dated issuer CSV for final values; locale PDF snapshots can differ.
- Primary URL: https://www.ishares.com/uk/individual/en/products/313193/ishares-moderate-portfolio-ucits-etf-modr
- Factsheet: https://www.ishares.com/gls-download/literature/fact-sheet/modr-ishares-moderate-portfolio-ucits-etf-fund-fact-sheet-en-gb.pdf

## MAGR — Growth Portfolio
- ISIN: IE00BLLZQ805; TER 0.25% in current candidate catalog.
- Candidate identity exists in repository research catalogue, but this audit has NOT independently revalidated current issuer page, CSV endpoint or holdings count. Keep as pending, not counted as verified.

## Direct CSV endpoint captured
- MACV: https://www.ishares.com/uk/individual/en/products/313196/ishares-conservative-portfolio-ucits-etf/latest-holdings.csv
- MODR: https://www.ishares.com/uk/individual/en/products/313193/ishares-moderate-portfolio-ucits-etf/latest-holdings.csv
The issuer page links directly to these endpoints. Retrieval from this environment returned HTTP 400 through the web gateway and a network download attempt failed; the files were therefore not obtained or inspected. Endpoint identity is confirmed, file accessibility/content is not.

## Technical next gate
1. Fetch the CSVs from the GitHub Actions runner (or a browser/network environment able to access BlackRock) and preserve dated raw samples.
2. Fetch raw CSV and preserve a dated immutable sample.
3. Validate encoding, headers, numeric/percentage formats, blank/cash rows, aggregate vs look-through rows.
4. Normalize holding identifiers and ticker/ISIN; distinguish ETF constituents from look-through securities.
5. Verify total weights including cash/derivatives and document tolerance (e.g. 98–102% only if source methodology justifies it).
6. Repeat fetch on a later date; confirm source URL stable and parser reproducible.
7. Only then promote to active holdings monitor.

**Conclusion:** MACV and MODR pass issuer-source/identity/CSV-control checks, but fail technical ingestion validation. MAGR remains a candidate awaiting dedicated revalidation.
