import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================
# NSE FUNDAMENTAL + MARKET VALIDATION SCANNER
# Version 1.0
# ============================================================

# -----------------------------
# SETTINGS
# -----------------------------

MIN_FINAL_SCORE = 75

# Test stocks for first run.
# Later we will connect the complete NSE universe.
TEST_STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "ITC.NS",
    "HDFCBANK.NS",
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_number(value):
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except:
        return None


def calculate_score(value, minimum, maximum=None):
    if value is None:
        return 0

    if value >= minimum:
        return 1

    return 0


# ============================================================
# PRICE TREND
# ============================================================

def price_trend_score(history):

    if history is None or len(history) < 220:
        return 0, {}

    close = history["Close"]

    ema20 = close.ewm(span=20, adjust=False).mean().iloc[-1]
    ema50 = close.ewm(span=50, adjust=False).mean().iloc[-1]
    ema200 = close.ewm(span=200, adjust=False).mean().iloc[-1]

    current_price = close.iloc[-1]

    price_3m_ago = close.iloc[-63] if len(close) >= 63 else None
    price_6m_ago = close.iloc[-126] if len(close) >= 126 else None

    return_3m = (
        ((current_price / price_3m_ago) - 1) * 100
        if price_3m_ago else None
    )

    return_6m = (
        ((current_price / price_6m_ago) - 1) * 100
        if price_6m_ago else None
    )

    score = 0

    # 1. Price > EMA20
    if current_price > ema20:
        score += 4

    # 2. EMA20 > EMA50
    if ema20 > ema50:
        score += 4

    # 3. EMA50 > EMA200
    if ema50 > ema200:
        score += 4

    # 4. 3 month return > 10%
    if return_3m is not None and return_3m > 10:
        score += 4

    # 5. 6 month return > 15%
    if return_6m is not None and return_6m > 15:
        score += 4

    details = {
        "price": current_price,
        "ema20": ema20,
        "ema50": ema50,
        "ema200": ema200,
        "return_3m": return_3m,
        "return_6m": return_6m,
    }

    return score, details


# ============================================================
# FUNDAMENTAL ANALYSIS
# ============================================================

def fundamental_score(info):

    score = 0

    revenue_growth = safe_number(
        info.get("revenueGrowth")
    )

    earnings_growth = safe_number(
        info.get("earningsGrowth")
    )

    roe = safe_number(
        info.get("returnOnEquity")
    )

    roce = None

    debt_equity = safe_number(
        info.get("debtToEquity")
    )

    pe = safe_number(
        info.get("tr
