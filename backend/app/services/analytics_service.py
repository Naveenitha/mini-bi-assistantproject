from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import SalesTransaction


def _completed_filter(q):
    return q.filter(SalesTransaction.status == "Completed")


def total_revenue(db: Session):
    val = _completed_filter(db.query(func.coalesce(func.sum(SalesTransaction.net_revenue), 0.0))).scalar()
    return float(val or 0.0)


def revenue_by_product(db: Session):
    rows = (
        _completed_filter(db.query(SalesTransaction.product, func.sum(SalesTransaction.net_revenue).label("rev")))
        .group_by(SalesTransaction.product)
        .order_by(func.sum(SalesTransaction.net_revenue).desc())
        .all()
    )
    return [{"product": r[0], "revenue": float(r[1])} for r in rows]


def highest_revenue_product(db: Session):
    data = revenue_by_product(db)
    if not data:
        return None
    return data[0]


def monthly_revenue(db: Session):
    # group by year-month
    rows = (
        _completed_filter(db.query(SalesTransaction.order_date, SalesTransaction.net_revenue))
        .all()
    )
    agg = {}
    for d, rev in rows:
        key = d.strftime("%Y-%m")
        agg[key] = agg.get(key, 0.0) + float(rev)
    result = [{"month": k, "revenue": round(v, 2)} for k, v in sorted(agg.items())]
    return result


def top_region(db: Session):
    rows = (
        _completed_filter(db.query(SalesTransaction.region, func.sum(SalesTransaction.net_revenue).label("rev")))
        .group_by(SalesTransaction.region)
        .order_by(func.sum(SalesTransaction.net_revenue).desc())
        .all()
    )
    data = [{"region": r[0], "revenue": float(r[1])} for r in rows]
    return data[0] if data else None


def compare_months(db: Session, month1: str, month2: str):
    mr = {m["month"]: m["revenue"] for m in monthly_revenue(db)}
    r1 = mr.get(month1)
    r2 = mr.get(month2)
    if r1 is None or r2 is None:
        return None
    change = r2 - r1
    if r1 == 0:
        pct = None
    else:
        pct = (change / r1) * 100.0
    return {
        "month1": month1,
        "month2": month2,
        "revenue_month1": r1,
        "revenue_month2": r2,
        "absolute_change": round(change, 2),
        "percentage_change": (round(pct, 2) if pct is not None else None),
    }
