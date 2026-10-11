# NSE Fundamental + Market Validation Scanner

This repository runs the **fundamental scanner**. The GitHub Actions workflow is scheduled for weekdays after the Indian cash market closes and can also be started manually.

## What it checks

- Fundamental score out of 60 across 11 criteria.
- Price trend score out of 20 using price/EMA20, EMA20/EMA50, EMA50/EMA200, 3-month return, and 6-month return.
- P/E re-rating score out of 20 when historical P/E observations are available.
- Data availability is reported separately. Missing fields are not silently treated as verified passes.
- Output: `final_scanner_results.csv`, attached to each workflow run as an artifact.

## Important data limitations in this free-data version

Yahoo Finance does not reliably provide every NSE fundamental field. In particular, this version does **not yet** source ROCE, promoter holding, promoter pledge, or historical P/E consistently. Those fields are shown as missing, and a stock cannot be labelled as fully qualified until the required data is verified. This is intentional: an incomplete row is not a buy recommendation.

PAT growth is calculated from the latest two annual net-income figures when available; it is not copied from EPS growth. Interest coverage is calculated from available income-statement figures when possible.

## Run modes

- Scheduled run: weekdays at 17:00 IST.
- Manual run: GitHub → Actions → Daily Fundamental Stock Scanner → Run workflow.
- Optional test run: set the workflow environment variable `SCAN_LIMIT` to a small number (for example, `25`) while checking data-source reliability. `0` means use the downloaded NSE equity universe.

## Interpretation

A high score is only a screening result, not a guarantee or a buy/sell instruction. Review latest company filings, valuation, liquidity, corporate actions, and risk before investing. Free public data may be delayed, incomplete, blocked, or inconsistent.
