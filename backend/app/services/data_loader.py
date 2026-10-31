import csv
import os
from datetime import datetime
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from app.config import CSV_PATH
from app.models import SalesTransaction

REQUIRED_COLUMNS = [
    "Transaction_Id", "Order_date", "Product", "Category", "Region",
    "Sales_channel", "Quantity", "Unit_price", "Discount_amount", "Status",
]

VALID_STATUSES = {"Completed", "Returned"}


def _parse_date(value: str):
    value = (value or "").strip()
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def load_csv_into_db(db: Session, csv_path: str = None) -> Dict:
    path = csv_path or CSV_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV file not found: {path}")

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in headers]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        rows = list(reader)

    # clear existing
    db.query(SalesTransaction).delete()
    db.commit()

    loaded = 0
    excluded: Dict[str, int] = {}
    seen_ids = set()

    def bump(reason):
        excluded[reason] = excluded.get(reason, 0) + 1

    for row in rows:
        tid = (row.get("Transaction_Id") or "").strip()
        # duplicate check
        if tid in seen_ids:
            bump("duplicate_transaction_id")
            continue
        # required fields
        product = (row.get("Product") or "").strip()
        category = (row.get("Category") or "").strip()
        region = (row.get("Region") or "").strip()
        channel = (row.get("Sales_channel") or "").strip()
        status = (row.get("Status") or "").strip()
        if not all([tid, product, category, region, channel, status]):
            bump("missing_required_text")
            continue
        if status not in VALID_STATUSES:
            bump("invalid_status")
            continue

        order_date = _parse_date(row.get("Order_date", ""))
        if order_date is None:
            bump("invalid_date")
            continue

        # quantity
        try:
            qty = int(float((row.get("Quantity") or "").strip()))
        except (ValueError, TypeError):
            bump("invalid_quantity")
            continue
        if qty <= 0:
            bump("non_positive_quantity")
            continue

        # unit price
        up_raw = (row.get("Unit_price") or "").strip()
        if up_raw == "":
            bump("missing_unit_price")
            continue
        try:
            unit_price = float(up_raw)
        except (ValueError, TypeError):
            bump("invalid_unit_price")
            continue
        if unit_price <= 0:
            bump("non_positive_unit_price")
            continue

        # discount
        try:
            discount = float((row.get("Discount_amount") or "0").strip() or 0)
        except (ValueError, TypeError):
            bump("invalid_discount")
            continue
        if discount < 0:
            bump("negative_discount")
            continue
        if discount > qty * unit_price:
            bump("excessive_discount")
            continue

        seen_ids.add(tid)
        net_revenue = qty * unit_price - discount
        rec = SalesTransaction(
            transaction_id=tid,
            order_date=order_date,
            product=product,
            category=category,
            region=region,
            sales_channel=channel,
            quantity=qty,
            unit_price=unit_price,
            discount_amount=discount,
            status=status,
            net_revenue=net_revenue,
        )
        db.add(rec)
        loaded += 1

    db.commit()
    return {
        "records_loaded": loaded,
        "records_excluded": sum(excluded.values()),
        "exclusion_reasons": excluded,
        "source_file": path,
    }
