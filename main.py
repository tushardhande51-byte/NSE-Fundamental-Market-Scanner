import os
import time
import warnings

import pandas as pd
import yfinance as yf

from fundamental_rules import fundamental_score
from market_validation import market_validation_score
from nse_universe import get_nse_universe

warnings.filterwarnings("ignore")

# Conservative qualification: missing data must never be treated as a pass.
MIN_FUNDAMENTAL_SCORE = 45
MIN_PRICE_SCORE = 14
MIN_PE_SCORE = 10
MIN_FINAL_SCORE = 75
MIN_DATA_COMPLETENESS = 8
REQUEST_PAUSE_SECONDS = 0.15

REQUIRED_FIELDS = [
    "revenue_growth", "eps_growth", "pat_growth", "roce", "roe",
    "debt_equity", "pe", "operating_margin", "promoter_holding",
    "promoter_pledge", "interest_coverage",
]


def safe_float(value):
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def statement_value(statement, row_names, column_index=0):
    """Find a financial-statement value by a list of possible row labels."""
    if statement is None or statement.empty or len(statement.columns) <= column_index:
        return None
    for row in row_names:
        if row in statement.index:
            return safe_float(statement.loc[row].iloc[column_index])
    return None


def growth_pct(latest, previous):
    latest = safe_float(latest)
    previous = safe_float(previous)
    if latest is None or previous is None or previous == 0:
        return None
    return (latest / previous - 1.0) * 100.0


def get_stock_data(symbol):
    print(f"Analyzing {symbol}...", flush=True)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        history = ticker.history(period="2y", auto_adjust=True, timeout=20)
        if history is None or history.empty:
            return {"Symbol": symbol, "Status": "DATA_ERROR", "Error": "No price history"}

        income = ticker.financials
        balance = ticker.balance_sheet

        # Do not duplicate EPS growth as PAT growth. Use reported annual net income.
        pat_latest = statement_value(income, ["Net Income", "Net Income Common Stockholders"], 0)
        pat_previous = statement_value(income, ["Net Income", "Net Income Common Stockholders"], 1)
        pat_growth = growth_pct(pat_latest, pat_previous)

        revenue_growth_raw = safe_float(info.get("revenueGrowth"))
        eps_growth_raw = safe_float(info.get("earningsGrowth"))
        roe_raw = safe_float(info.get("returnOnEquity"))
        debt_equity_raw = safe_float(info.get("debtToEquity"))
        margin_raw = safe_float(info.get("operatingMargins"))

        ebit = statement_value(income, ["EBIT", "Operating Income"], 0)
        interest_expense = statement_value(income, ["Interest Expense", "Interest Expense Non Operating"], 0)
        interest_coverage = None
        if ebit is not None and interest_expense is not None and interest_expense != 0:
            interest_coverage = abs(ebit / interest_expense)

        # ROCE is not consistently exposed in Yahoo's company summary.
        # Do not fabricate it from ROE. Promoter data is sourced from filings,
        # not Yahoo Finance, and remains explicitly missing in this free-data version.
        data = {
            "revenue_growth": revenue_growth_raw * 100 if revenue_growth_raw is not None else None,
            "eps_growth": eps_growth_raw * 100 if eps_growth_raw is not None else None,
            "pat_growth": pat_growth,
            "roce": None,
            "roe": roe_raw * 100 if roe_raw is not None else None,
            "debt_equity": debt_equity_raw / 100 if debt_equity_raw is not None else None,
            "pe": safe_float(info.get("trailingPE")),
            "operating_margin": margin_raw * 100 if margin_raw is not None else None,
            "promoter_holding": None,
            "promoter_pledge": None,
            "interest_coverage": interest_coverage,
        }

        fund_score, fund_results = fundamental_score(data)
        known_fields = sum(data.get(field) is not None for field in REQUIRED_FIELDS)
        missing_fields = [field for field in REQUIRED_FIELDS if data.get(field) is None]

        # Historical P/E series is not available from the current free Yahoo source.
        # Keep it missing; do not pretend P/E re-rating was verified.
        market = market_validation_score(
            history=history,
            current_pe=data["pe"],
            pe_3m_ago=None,
            pe_6m_ago=None,
            pe_12m_ago=None,
            eps_growth=data["eps_growth"],
        )

        price_score = market["price_score"]
        pe_score = market["pe_score"]
        market_score = market["market_validation_score"]
        final_score = fund_score + market_score

        qualified = (
            known_fields >= MIN_DATA_COMPLETENESS
            and not missing_fields
            and fund_score >= MIN_FUNDAMENTAL_SCORE
            and price_score >= MIN_PRICE_SCORE
            and pe_score >= MIN_PE_SCORE
            and final_score >= MIN_FINAL_SCORE
        )

        if known_fields < MIN_DATA_COMPLETENESS or missing_fields:
            status = "INCOMPLETE_DATA"
        elif qualified and final_score >= 85:
            status = "EXCEPTIONAL"
        elif qualified:
            status = "STRONG"
        elif final_score >= 65:
            status = "WATCHLIST"
        else:
            status = "REJECT"

        details = market.get("price_details", {})
        return {
            "Symbol": symbol,
            "Price": round(details.get("price"), 2) if details.get("price") is not None else None,
            "Fundamental Score /60": fund_score,
            "Price Trend /20": price_score,
            "P/E Re-rating /20": pe_score,
            "Market Score /40": market_score,
            "Final Score /100": final_score,
            "Data Fields Available /11": known_fields,
            "Missing Fields": ", ".join(missing_fields),
            "Status": status,
            "Qualified": qualified,
            "Market Re-rating Verified": market["market_rerating"],
            "P/E": data["pe"],
            "Revenue Growth %": data["revenue_growth"],
            "EPS Growth %": data["eps_growth"],
            "PAT Growth %": data["pat_growth"],
            "ROCE %": data["roce"],
            "ROE %": data["roe"],
            "Debt/Equity": data["debt_equity"],
            "Operating Margin %": data["operating_margin"],
            "Interest Coverage": data["interest_coverage"],
            "Promoter Holding %": data["promoter_holding"],
            "Promoter Pledge %": data["promoter_pledge"],
            "3M Return %": round(details.get("return_3m"), 2) if details.get("return_3m") is not None else None,
            "6M Return %": round(details.get("return_6m"), 2) if details.get("return_6m") is not None else None,
            "Error": "",
        }
    except Exception as exc:
        print(f"ERROR {symbol}: {exc}", flush=True)
        return {"Symbol": symbol, "Status": "DATA_ERROR", "Error": str(exc)[:250]}


def main():
    print("=" * 78)
    print("NSE FUNDAMENTAL + MARKET VALIDATION SCANNER")
    print("Missing data is flagged; it is never treated as a verified pass.")
    print("=" * 78)

    symbols = get_nse_universe()
    if not symbols:
        # Small fallback is for troubleshooting only; clearly mark this run as limited.
        symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "ITC.NS", "HDFCBANK.NS"]
        print("WARNING: NSE universe download failed; running 5-stock diagnostic only.")

    limit = safe_float(os.getenv("SCAN_LIMIT", "0")) or 0
    if limit > 0:
        symbols = symbols[:int(limit)]
        print(f"TEST MODE: scanning only {len(symbols)} symbols.")

    print(f"Stocks queued: {len(symbols)}")
    results = []
    for index, symbol in enumerate(symbols, start=1):
        result = get_stock_data(symbol)
        if result is not None:
            results.append(result)
        if index % 25 == 0:
            print(f"Progress: {index}/{len(symbols)}", flush=True)
        time.sleep(REQUEST_PAUSE_SECONDS)

    if not results:
        raise RuntimeError("No stock results were produced; inspect data-source/network errors.")

    df = pd.DataFrame(results)
    if "Final Score /100" in df.columns:
        df = df.sort_values("Final Score /100", ascending=False, na_position="last")

    df.to_csv("final_scanner_results.csv", index=False)
    qualified = df[df.get("Qualified", pd.Series(False, index=df.index)) == True]
    watchlist = df[df.get("Status", pd.Series("", index=df.index)) == "WATCHLIST"]

    print("\n" + "=" * 78)
    print(f"Stocks processed: {len(df)}")
    print(f"Qualified stocks: {len(qualified)}")
    print(f"Watchlist stocks: {len(watchlist)}")
    print(f"Rows with incomplete/missing data: {int((df.get('Status', pd.Series(dtype=str)) == 'INCOMPLETE_DATA').sum())}")
    print("Saved: final_scanner_results.csv")
    print("NOTE: Current free source does not supply all promoter metrics or historical P/E.")
    print("A stock cannot qualify until required fields and P/E re-rating data are verified.")


if __name__ == "__main__":
    main()
