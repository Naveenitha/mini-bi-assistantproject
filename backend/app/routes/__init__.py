from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AskRequest, AskResponse
from app.services.question_parser import parse_question
from app.services.analytics_service import (
    total_revenue, highest_revenue_product, monthly_revenue, top_region, compare_months,
)
from app.services.data_loader import load_csv_into_db
from app.services.llm_service import explain
from app.config import CSV_PATH

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "app": "Mini AI Business Intelligence Assistant"}


@router.get("/api/data-status")
def data_status(db: Session = Depends(get_db)):
    from app.models import SalesTransaction
    count = db.query(SalesTransaction).count()
    return {
        "records_loaded": count,
        "records_excluded": 0,
        "source_file": CSV_PATH,
    }


@router.post("/api/load-data")
def load_data(db: Session = Depends(get_db)):
    try:
        info = load_csv_into_db(db, CSV_PATH)
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest, db: Session = Depends(get_db)):
    op, params = parse_question(req.question)
    if op is None:
        answer = ("I can only answer supported analytics questions: total revenue, "
                  "highest-revenue product, monthly revenue trend, top region, "
                  "and revenue change between two months.")
        return AskResponse(
            question=req.question,
            operation="unsupported",
            answer=answer,
            metrics={},
            supporting_data=[],
            data_quality={"records_loaded": db.query(__import__("app.models", fromlist=["SalesTransaction"]).SalesTransaction).count()},
            ai={"used": False, "mode": "deterministic_fallback"},
        )

    if op == "total_revenue":
        val = total_revenue(db)
        metrics = {"total_revenue": val, "currency": "not specified"}
        supporting = []
        summary = f"Total revenue is {val}."
    elif op == "highest_revenue_product":
        r = highest_revenue_product(db)
        metrics = {"product": r["product"], "revenue": r["revenue"]} if r else {}
        supporting = [r] if r else []
        summary = f"Highest revenue product is {r['product']} with {r['revenue']}." if r else "No data."
    elif op == "monthly_revenue":
        data = monthly_revenue(db)
        metrics = {"months": len(data)}
        supporting = data
        summary = "Monthly revenue trend returned."
    elif op == "top_region":
        r = top_region(db)
        metrics = {"region": r["region"], "revenue": r["revenue"]} if r else {}
        supporting = [r] if r else []
        summary = f"Top region is {r['region']} with {r['revenue']}." if r else "No data."
    elif op == "compare_months":
        m1 = params["month1"]; m2 = params["month2"]
        # validate months exist
        res = compare_months(db, m1, m2)
        if res is None:
            raise HTTPException(status_code=400, detail="One or both months not found in data.")
        metrics = res
        supporting = []
        summary = (f"Revenue changed from {res['revenue_month1']} in {m1} to "
                   f"{res['revenue_month2']} in {m2}: {res['absolute_change']} "
                   f"({res['percentage_change']}%).")
    else:
        raise HTTPException(status_code=400, detail="Unsupported operation.")

    text, used, mode = explain(req.question, summary)
    from app.models import SalesTransaction
    loaded = db.query(SalesTransaction).count()
    return AskResponse(
        question=req.question,
        operation=op,
        answer=text,
        metrics=metrics,
        supporting_data=supporting,
        data_quality={"records_loaded": loaded},
        ai={"used": used, "mode": mode},
    )
