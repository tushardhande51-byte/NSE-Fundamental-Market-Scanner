import yfinance as yf
import pandas as pd
from fundamental_rules import fundamental_score
from market_validation import market_validation_score

# ============================================================
# NSE FUNDAMENTAL + MARKET VALIDATION MASTER SCANNER
# FINAL SCORE = 100
# ============================================================

TEST_STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "ITC.NS",
    "HDFCBANK.NS",
]

MIN_FUNDAMENTAL_SCORE = 45
MIN_PRICE_SCORE = 14
MIN_PE_SCORE = 10
MIN_FINAL_SCORE = 75


def safe_float(value):
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except:
        return None


def get_stock_data(symbol):

    print(f"Analyzing {symbol}...")

    try:

        ticker = yf.Ticker(symbol)

        info = ticker.info

        history = ticker.history(
            period="2y",
            auto_adjust=True
        )

        if history.empty:
            return None

        # ----------------------------------------------------
        # FUNDAMENTAL DATA
        # ----------------------------------------------------

        data = {
            "revenue_growth": (
                safe_float(info.get("revenueGrowth")) * 100
                if info.get("revenueGrowth") is not None
                else None
            ),

            "eps_growth": (
                safe_float(info.get("earningsGrowth")) * 100
                if info.get("earningsGrowth") is not None
                else None
            ),

            "pat_growth": (
                safe_float(info.get("earningsGrowth")) * 100
                if info.get("earningsGrowth") is not None
                else None
            ),

            "roce": None,

            "roe": (
                safe_float(info.get("returnOnEquity")) * 100
                if info.get("returnOnEquity") is not None
                else None
            ),

            "debt_equity": (
                safe_float(info.get("debtToEquity")) / 100
                if info.get("debtToEquity") is not None
                else None
            ),

            "pe": safe_float(
                info.get("trailingPE")
            ),

            "operating_margin": (
                safe_float(info.get("operatingMargins")) * 100
                if info.get("operatingMargins") is not None
                else None
            ),

            "promoter_holding": None,

            "promoter_pledge": None,

            "interest_coverage": None,
        }

        # ----------------------------------------------------
        # FUNDAMENTAL SCORE
        # ----------------------------------------------------

        fund_score, fund_results = fundamental_score(
            data
        )

        # ----------------------------------------------------
        # HISTORICAL P/E
        #
        # Yahoo Finance does not reliably provide historical
        # P/E directly.
        #
        # We therefore leave these fields as None for now.
        # A dedicated historical valuation data source will
        # be connected in the next version.
        # ----------------------------------------------------

        current_pe = data["pe"]

        pe_3m = None
        pe_6m = None
        pe_12m = None

        # ----------------------------------------------------
        # MARKET VALIDATION
        # ----------------------------------------------------

        market = market_validation_score(
            history=history,
            current_pe=current_pe,
            pe_3m_ago=pe_3m,
            pe_6m_ago=pe_6m,
            pe_12m_ago=pe_12m,
            eps_growth=data["eps_growth"]
        )

        price_score = market["price_score"]
        pe_score = market["pe_score"]

        market_score = market[
            "market_validation_score"
        ]

        final_score = (
            fund_score +
            market_score
        )

        # ----------------------------------------------------
        # FINAL STATUS
        # ----------------------------------------------------

        if (
            fund_score >= MIN_FUNDAMENTAL_SCORE
            and price_score >= MIN_PRICE_SCORE
            and pe_score >= MIN_PE_SCORE
            and final_score >= MIN_FINAL_SCORE
        ):

            qualified = True

        else:

            qualified = False

        if final_score >= 85:
            status = "EXCEPTIONAL"

        elif final_score >= 75:
            status = "STRONG"

        elif final_score >= 65:
            status = "GOOD"

        elif final_score >= 55:
            status = "WATCHLIST"

        else:
            status = "REJECT"

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        return {
            "Symbol": symbol,

            "Price": round(
                market["price_details"].get(
                    "price", 0
                ),
                2
            ),

            "Fundamental": fund_score,

            "Price Trend": price_score,

            "P/E Score": pe_score,

            "Market Validation": market_score,

            "Final Score": final_score,

            "Status": status,

            "Qualified": qualified,

            "Market Re-rating": market[
                "market_rerating"
            ],

            "P/E": data["pe"],

            "EPS Growth %": data[
                "eps_growth"
            ],

            "ROE %": data["roe"],

            "Debt/Equity": data[
                "debt_equity"
            ],

            "3M Return %": round(
                market["price_details"].get(
                    "return_3m", 0
                ),
                2
            ),

            "6M Return %": round(
                market["price_details"].get(
                    "return_6m", 0
                ),
                2
            ),
        }

    except Exception as e:

        print(
            f"ERROR {symbol}: {e}"
        )

        return None


def main():

    print()
    print("=" * 80)
    print(
        "NSE FUNDAMENTAL + MARKET VALIDATION SCANNER"
    )
    print("=" * 80)
    print()

    results = []

    for symbol in TEST_STOCKS:

        result = get_stock_data(symbol)

        if result is not None:

            results.append(result)

    if not results:

        print(
            "No stocks could be analyzed."
        )

        return

    df = pd.DataFrame(results)

    # Highest score first
    df = df.sort_values(
        "Final Score",
        ascending=False
    )

    print()
    print("=" * 80)
    print("ALL STOCKS")
    print("=" * 80)

    print(
        df.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # QUALIFIED STOCKS
    # --------------------------------------------------------

    qualified = df[
        df["Qualified"] == True
    ]

    print()
    print("=" * 80)
    print("QUALIFIED STOCKS")
    print("=" * 80)

    if qualified.empty:

        print(
            "No stock passed all minimum conditions."
        )

    else:

        print(
            qualified.to_string(
                index=False
            )
        )

    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    df.to_csv(
        "final_scanner_results.csv",
        index=False
    )

    print()
    print(
        "Results saved to final_scanner_results.csv"
    )


if __name__ == "__main__":
    main()
