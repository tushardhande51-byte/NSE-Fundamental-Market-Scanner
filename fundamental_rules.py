# ============================================================
# NSE FUNDAMENTAL RULES
# 11 PARAMETERS / 60 POINTS
# Promoter holding and pledge trends: latest 3 quarters
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


def _trend_values(data, key):
    """Return numeric quarterly values, newest quarter first.
    Example: [latest, previous, two_quarters_ago].
    Missing or invalid values are ignored only by rejecting the trend
    calculation; they are never treated as zero.
    """
    values = data.get(key)
    if not isinstance(values, (list, tuple)) or len(values) < 3:
        return None
    parsed = [safe_float(v) for v in values[:3]]
    if any(v is None for v in parsed):
        return None
    return parsed


def fundamental_score(data):
    """
    Fundamental score = 60 points.

    Core criteria:
    Revenue Growth 8; EPS Growth 8; PAT Growth 7; ROCE 6; ROE 6;
    Debt/Equity 6; P/E 5; Operating Margin 4; Promoter Holding 4;
    Promoter Pledge 3; Interest Coverage 3.

    Promoter Holding (4 points):
      - 1 point if current holding >= 50%
      - 3 points if holding is stable/rising over the latest 3 quarters
        (latest quarter compared with two quarters earlier).

    Promoter Pledge (3 points):
      - 1 point if current pledge is 0%
      - 2 points if pledge has fallen over the latest 3 quarters.

    Quarterly inputs (when available):
      promoter_holding_qoq = [latest_pct, previous_pct, two_quarters_ago_pct]
      promoter_pledge_qoq  = [latest_pct, previous_pct, two_quarters_ago_pct]
    Pledge should use one consistent definition/source across all quarters.
    """

    score = 0
    results = {}

    revenue_growth = safe_float(data.get("revenue_growth"))
    if check_min(revenue_growth, 20):
        score += 8
        results["Revenue Growth"] = True
    else:
        results["Revenue Growth"] = False

    eps_growth = safe_float(data.get("eps_growth"))
    if check_min(eps_growth, 20):
        score += 8
        results["EPS Growth"] = True
    else:
        results["EPS Growth"] = False

    pat_growth = safe_float(data.get("pat_growth"))
    if check_min(pat_growth, 20):
        score += 7
        results["PAT Growth"] = True
    else:
        results["PAT Growth"] = False

    roce = safe_float(data.get("roce"))
    if check_min(roce, 15):
        score += 6
        results["ROCE"] = True
    else:
        results["ROCE"] = False

    roe = safe_float(data.get("roe"))
    if check_min(roe, 15):
        score += 6
        results["ROE"] = True
    else:
        results["ROE"] = False

    debt_equity = safe_float(data.get("debt_equity"))
    if check_max(debt_equity, 0.50):
        score += 6
        results["Debt/Equity"] = True
    else:
        results["Debt/Equity"] = False

    pe = safe_float(data.get("pe"))
    if check_max(pe, 15) and pe is not None and pe > 0:
        score += 5
        results["P/E"] = True
    else:
        results["P/E"] = False

    operating_margin = safe_float(data.get("operating_margin"))
    if check_min(operating_margin, 15):
        score += 4
        results["Operating Margin"] = True
    else:
        results["Operating Margin"] = False

    # Promoter holding: level is a small part of the score; trend matters more.
    promoter_holding = safe_float(data.get("promoter_holding"))
    holding_points = 0
    if check_min(promoter_holding, 50):
        holding_points += 1

    holding_trend = _trend_values(data, "promoter_holding_qoq")
    if holding_trend is not None:
        latest, previous, oldest = holding_trend
        # Stable means no more than a 0.5 percentage-point decline
        # from two quarters ago. Small changes may be reporting noise.
        if latest >= oldest - 0.5:
            holding_points += 3
            results["Promoter Holding Trend"] = "STABLE_OR_RISING"
        else:
            results["Promoter Holding Trend"] = "FALLING_CHECK_REASON"
    else:
        results["Promoter Holding Trend"] = "DATA_UNAVAILABLE"

    score += holding_points
    results["Promoter Holding"] = {
        "points": holding_points,
        "max_points": 4,
        "current_pct": promoter_holding,
    }

    # Promoter pledge: zero pledge earns 1 point; declining pledge earns 2.
    promoter_pledge = safe_float(data.get("promoter_pledge"))
    pledge_points = 0
    if promoter_pledge is not None and promoter_pledge == 0:
        pledge_points += 1

    pledge_trend = _trend_values(data, "promoter_pledge_qoq")
    if pledge_trend is not None:
        latest, previous, oldest = pledge_trend
        if latest < oldest:
            pledge_points += 2
            results["Promoter Pledge Trend"] = "FALLING_POSITIVE"
        elif latest == oldest:
            results["Promoter Pledge Trend"] = "STABLE"
        else:
            results["Promoter Pledge Trend"] = "RISING_WARNING"
    else:
        results["Promoter Pledge Trend"] = "DATA_UNAVAILABLE"

    score += pledge_points
    results["Promoter Pledge"] = {
        "points": pledge_points,
        "max_points": 3,
        "current_pct": promoter_pledge,
    }

    interest_coverage = safe_float(data.get("interest_coverage"))
    if check_min(interest_coverage, 5):
        score += 3
        results["Interest Coverage"] = True
    else:
        results["Interest Coverage"] = False

    return score, results
