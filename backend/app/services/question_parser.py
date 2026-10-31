import re
from typing import Dict, Optional, Tuple

MONTHS = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}


def _normalize_month_token(tok: str) -> Optional[str]:
    tok = tok.strip().lower()
    if tok in MONTHS:
        return "2026-" + MONTHS[tok]
    m = re.match(r"(\d{4})-(\d{2})", tok)
    if m:
        return tok
    m = re.match(r"(\d{1,2})/(\d{4})", tok)
    if m:
        return f"{m.group(2)}-{int(m.group(1)):02d}"
    return None


def parse_question(question: str) -> Tuple[Optional[str], Dict]:
    q = question.strip().lower()
    if not q:
        return None, {}

    if "total revenue" in q or q == "revenue":
        return "total_revenue", {}

    if "highest revenue product" in q or "top product" in q or ("product" in q and "highest" in q and "revenue" in q):
        return "highest_revenue_product", {}

    if "monthly revenue" in q or "revenue trend" in q or "monthly trend" in q:
        return "monthly_revenue", {}

    if "region" in q and ("highest" in q or "top" in q):
        return "top_region", {}

    # month comparison: "how did revenue change between january and february"
    m = re.search(r"between\s+(\w+)\s+and\s+(\w+)", q)
    if m and "revenue" in q and ("change" in q or "compare" in q or "between" in q):
        a = _normalize_month_token(m.group(1))
        b = _normalize_month_token(m.group(2))
        if a and b:
            return "compare_months", {"month1": a, "month2": b}

    # also handle "january vs february"
    m = re.search(r"(\w+)\s+(?:vs|versus)\s+(\w+)", q)
    if m and "revenue" in q:
        a = _normalize_month_token(m.group(1))
        b = _normalize_month_token(m.group(2))
        if a and b:
            return "compare_months", {"month1": a, "month2": b}

    return None, {}
