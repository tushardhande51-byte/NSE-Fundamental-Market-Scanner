# NSE Fundamental + Market Validation Scanner

This repository scans the NSE equity universe and reports three business-development categories alongside the existing 11-parameter fundamental score and 40-point market validation score.

## Three business categories
- **A_COMPOUNDER:** established profitability and return ratios. Requires observed revenue growth, positive PAT growth, ROCE >= 15%, ROE >= 15%, debt/equity <= 0.5 and operating margin >= 10%.
- **B_EMERGING_GROWTH:** revenue growth >= 15% plus positive EBITDA margin or improving quarterly EBITDA; positive PAT and a usable P/E are not mandatory. Debt/equity above 1.0 blocks this classification when known.
- **C_TURNAROUND:** latest three reported quarters show sequentially improving revenue and either EBITDA or PAT. This is an evidence-based early recovery flag, not a buy signal.
- **UNCLASSIFIED:** evidence is insufficient. Missing data is never assumed to pass.

## Existing scoring retained
- Fundamental score: 60 points across 11 criteria.
- Price trend score: 20 points (price/EMA20, EMA20/EMA50, EMA50/EMA200, 3-month return, 6-month return).
- P/E re-rating score: 20 points when historical observations exist.
- Final score: 100 points. Category classification is separate from the score and does not bypass data-quality checks.

## Data limitations
Yahoo Finance may not reliably expose ROCE, promoter holding, promoter pledge, quarterly EBITDA, or historical P/E for every NSE company. Missing fields remain N/A / DATA_UNAVAILABLE. Category B can be assigned without positive PAT only when the available revenue and EBITDA evidence meets the stated rules. Category C requires sequential quarterly statement evidence. No missing field is imputed.

The free-data version calculates PAT growth from reported annual net income where available. It does not fabricate ROCE from ROE or treat unavailable promoter data as zero.

## Output and run modes
- CSV artifact: `final_scanner_results.csv`
- Scheduled/manual GitHub Actions behavior is unchanged.
- `SCAN_LIMIT=25` runs a small diagnostic sample; `0` scans the downloaded NSE equity universe.
- Telegram delivery remains optional and uses the existing repository secrets.

## Interpretation
Categories are screening labels, not buy/sell recommendations. A high score or category label does not establish fair value, future profitability, or safety. Review company filings, cash flow, debt, dilution, valuation, liquidity and execution risks before investing.
