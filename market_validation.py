# ============================================================
# MARKET VALIDATION ENGINE
# PRICE TREND = 20 POINTS
# P/E RE-RATING = 20 POINTS
# TOTAL = 40 POINTS
# ============================================================

import pandas as pd


# ============================================================
# PRICE TREND SCORE
# ============================================================

def price_trend_score(history):

    if history is None or history.empty:
        return 0, {}

    if len(history) < 220:
        return 0, {}

    close = history["Close"].dropna()

    if len(close) < 220:
        return 0, {}

    # EMA calculations
    ema20 = close.ewm(
        span=20,
        adjust=False
    ).mean().iloc[-1]

    ema50 = close.ewm(
        span=50,
        adjust=False
    ).mean().iloc[-1]

    ema200 = close.ewm(
        span=200,
        adjust=False
    ).mean().iloc[-1]

    current_price = close.iloc[-1]

    # 3-month and 6-month prices
    price_3m_ago = close.iloc[-63]
    price_6m_ago = close.iloc[-126]

    return_3m = (
        (current_price / price_3m_ago) - 1
    ) * 100

    return_6m = (
        (current_price / price_6m_ago) - 1
    ) * 100

    score = 0

    # --------------------------------------------------------
    # 1. PRICE > EMA20 = 4 POINTS
    # --------------------------------------------------------

    if current_price > ema20:
        score += 4

    # --------------------------------------------------------
    # 2. EMA20 > EMA50 = 4 POINTS
    # --------------------------------------------------------

    if ema20 > ema50:
        score += 4

    # --------------------------------------------------------
    # 3. EMA50 > EMA200 = 4 POINTS
    # --------------------------------------------------------

    if ema50 > ema200:
        score += 4

    # --------------------------------------------------------
    # 4. 3-MONTH RETURN > 10% = 4 POINTS
    # --------------------------------------------------------

    if return_3m > 10:
        score += 4

    # --------------------------------------------------------
    # 5. 6-MONTH RETURN > 15% = 4 POINTS
    # --------------------------------------------------------

    if return_6m > 15:
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
# P/E RE-RATING SCORE
# ============================================================

def pe_rerating_score(
    current_pe,
    pe_3m_ago=None,
    pe_6m_ago=None,
    pe_12m_ago=None,
    eps_growth=None
):

    score = 0

    current_pe = safe_float(current_pe)
    pe_3m_ago = safe_float(pe_3m_ago)
    pe_6m_ago = safe_float(pe_6m_ago)
    pe_12m_ago = safe_float(pe_12m_ago)
    eps_growth = safe_float(eps_growth)

    # --------------------------------------------------------
    # 1. CURRENT P/E > 3 MONTH AGO = 5 POINTS
    # --------------------------------------------------------

    if (
        current_pe is not None
        and pe_3m_ago is not None
        and pe_3m_ago > 0
        and current_pe > pe_3m_ago
    ):
        score += 5

    # --------------------------------------------------------
    # 2. CURRENT P/E > 6 MONTH AGO = 5 POINTS
    # --------------------------------------------------------

    if (
        current_pe is not None
        and pe_6m_ago is not None
        and pe_6m_ago > 0
        and current_pe > pe_6m_ago
    ):
        score += 5

    # --------------------------------------------------------
    # 3. CURRENT P/E > 12 MONTH AGO = 5 POINTS
    # --------------------------------------------------------

    if (
        current_pe is not None
        and pe_12m_ago is not None
        and pe_12m_ago > 0
        and current_pe > pe_12m_ago
    ):
        score += 5

    # --------------------------------------------------------
    # 4. EPS GROWTH >= P/E GROWTH = 5 POINTS
    # --------------------------------------------------------

    if (
        current_pe is not None
        and pe_12m_ago is not None
        and pe_12m_ago > 0
        and eps_growth is not None
    ):

        pe_growth = (
            (current_pe / pe_12m_ago) - 1
        ) * 100

        if eps_growth >= pe_growth:
            score += 5

    else:
        pe_growth = None

    # --------------------------------------------------------
    # P/E OVER-EXPANSION PENALTY
    # --------------------------------------------------------

    penalty = 0

    if (
        pe_growth is not None
        and eps_growth is not None
        and pe_growth > (eps_growth * 2)
    ):
        penalty = 5
        score = max(0, score - penalty)

    details = {
        "current_pe": current_pe,
        "pe_3m_ago": pe_3m_ago,
        "pe_6m_ago": pe_6m_ago,
        "pe_12m_ago": pe_12m_ago,
        "eps_growth": eps_growth,
        "pe_growth": pe_growth,
        "penalty": penalty,
    }

    return score, details


# ============================================================
# HELPER
# ============================================================

def safe_float(value):

    try:

        if value is None:
            return None

        if pd.isna(value):
            return None

        return float(value)

    except (TypeError, ValueError):

        return None


# ============================================================
# MARKET VALIDATION
# ============================================================

def market_validation_score(
    history,
    current_pe,
    pe_3m_ago=None,
    pe_6m_ago=None,
    pe_12m_ago=None,
    eps_growth=None
):

    # Price Trend
    price_score, price_details = price_trend_score(
        history
    )

    # P/E Re-rating
    pe_score, pe_details = pe_rerating_score(
        current_pe=current_pe,
        pe_3m_ago=pe_3m_ago,
        pe_6m_ago=pe_6m_ago,
        pe_12m_ago=pe_12m_ago,
        eps_growth=eps_growth
    )

    total_score = price_score + pe_score

    # --------------------------------------------------------
    # MARKET RE-RATING FLAG
    # --------------------------------------------------------

    market_rerating = False

    if (
        price_score >= 14
        and pe_score >= 10
        and eps_growth is not None
        and eps_growth > 0
    ):
        market_rerating = True

    return {
        "price_score": price_score,
        "pe_score": pe_score,
        "market_validation_score": total_score,
        "market_rerating": market_rerating,
        "price_details": price_details,
        "pe_details": pe_details,
    }
