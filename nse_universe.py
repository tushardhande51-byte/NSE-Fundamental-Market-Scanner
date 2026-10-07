import pandas as pd
from io import StringIO
import requests

# ============================================================
# NSE STOCK UNIVERSE
# ============================================================

NSE_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"


def get_nse_universe():

    print("Downloading NSE stock universe...")

    try:
        response = requests.get(
            NSE_URL,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        df = pd.read_csv(
            StringIO(response.text)
        )

        symbols = []

        for symbol in df["SYMBOL"].dropna():

            symbol = str(symbol).strip()

            if symbol:
                symbols.append(
                    symbol + ".NS"
                )

        symbols = sorted(
            list(set(symbols))
        )

        print(
            f"NSE stocks found: {len(symbols)}"
        )

        return symbols

    except Exception as e:

        print(
            f"Error downloading NSE universe: {e}"
        )

        return []


if __name__ == "__main__":

    stocks = get_nse_universe()

    print()
    print(
        "First 20 stocks:"
    )

    for stock in stocks[:20]:
        print(stock)

    print()
    print(
        f"Total stocks: {len(stocks)}"
    )
