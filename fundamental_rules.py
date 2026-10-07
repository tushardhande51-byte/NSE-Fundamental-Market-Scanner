# ============================================================
# NSE FUNDAMENTAL RULES
# 11 PARAMETERS / 60 POINTS
# ============================================================

def safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def check_min(value, minimum):
    return value is not None and value >= minimum


def check_max(value, maximum):
    return value is not None and value <= maximum


def fundamental_score(data):
    """
    Fundamental score = 60 points

    Parameters:
    1. Revenue Growth       8
    2. EPS Growth           8
    3. PAT Growth           7
    4. ROCE                 6
    5. ROE                  6
    6. Debt/Equity          6
    7. P/E                  5
    8. Operating Margin     4
    9. Promoter Holding     4
    10. Promoter Pledge     3
    11. Interest Coverage   3
    """

    score = 0
    results = {}

    # --------------------------------------------------------
    # 1. REVENUE GROWTH >= 20%  → 8 POINTS
    # --------------------------------------------------------

    revenue_growth = safe_float(data.get("revenue_growth"))

    if check_min(revenue_growth, 20):
        score += 8
        results["Revenue Growth"] = True
    else:
        results["Revenue Growth"] = False

    # --------------------------------------------------------
    # 2. EPS GROWTH >= 20%  → 8 POINTS
    # --------------------------------------------------------

    eps_growth = safe_float(data.get("eps_growth"))

    if check_min(eps_growth, 20):
        score += 8
        results["EPS Growth"] = True
    else:
        results["EPS Growth"] = False

    # --------------------------------------------------------
    # 3. PAT GROWTH >= 20%  → 7 POINTS
    # --------------------------------------------------------

    pat_growth = safe_float(data.get("pat_growth"))

    if check_min(pat_growth, 20):
        score += 7
        results["PAT Growth"] = True
    else:
        results["PAT Growth"] = False

    # --------------------------------------------------------
    # 4. ROCE >= 15%  → 6 POINTS
    # --------------------------------------------------------

    roce = safe_float(data.get("roce"))

    if check_min(roce, 15):
        score += 6
        results["ROCE"] = True
    else:
        results["ROCE"] = False

    # --------------------------------------------------------
    # 5. ROE >= 15%  → 6 POINTS
    # --------------------------------------------------------

    roe = safe_float(data.get("roe"))

    if check_min(roe, 15):
        score += 6
        results["ROE"] = True
    else:
        results["ROE"] = False

    # --------------------------------------------------------
    # 6. DEBT / EQUITY <= 0.50  → 6 POINTS
    # --------------------------------------------------------

    debt_equity = safe_float(data.get("debt_equity"))

    if check_max(debt_equity, 0.50):
        score += 6
        results["Debt/Equity"] = True
    else:
        results["Debt/Equity"] = False

    # --------------------------------------------------------
    # 7. P/E <= 15  → 5 POINTS
    # --------------------------------------------------------

    pe = safe_float(data.get("pe"))

    if check_max(pe, 15):
        score += 5
        results["P/E"] = True
    else:
        results["P/E"] = False

    # --------------------------------------------------------
    # 8. OPERATING MARGIN >= 15%  → 4 POINTS
    # --------------------------------------------------------

    operating_margin = safe_float(
        data.get("operating_margin")
    )

    if check_min(operating_margin, 15):
        score += 4
        results["Operating Margin"] = True
    else:
        results["Operating Margin"] = False

    # --------------------------------------------------------
    # 9. PROMOTER HOLDING >= 50%  → 4 POINTS
    # --------------------------------------------------------

    promoter_holding = safe_float(
        data.get("promoter_holding")
    )

    if check_min(promoter_holding, 50):
        score += 4
        results["Promoter Holding"] = True
    else:
        results["Promoter Holding"] = False

    # --------------------------------------------------------
    # 10. PROMOTER PLEDGE = 0%  → 3 POINTS
    # --------------------------------------------------------

    promoter_pledge = safe_float(
        data.get("promoter_pledge")
    )

    if promoter_pledge is not None and promoter_pledge == 0:
        score += 3
        results["Promoter Pledge"] = True
    else:
        results["Promoter Pledge"] = False

    # --------------------------------------------------------
    # 11. INTEREST COVERAGE >= 5x  → 3 POINTS
    # --------------------------------------------------------

    interest_coverage = safe_float(
        data.get("interest_coverage")
    )

    if check_min(interest_coverage, 5):
        score += 3
        results["Interest Coverage"] = True
    else:
        results["Interest Coverage"] = False

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    return score, results
