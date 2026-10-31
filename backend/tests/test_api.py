import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.services.data_loader import load_csv_into_db

# temp db
fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.remove(db_path)
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def seed():
    db = TestingSession()
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "ai_bi_assistant_sales_data - GET.csv")
    csv_path = os.path.abspath(csv_path)
    load_csv_into_db(db, csv_path)
    db.close()
    yield
    try:
        os.remove(db_path)
    except OSError:
        pass


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_data_status():
    r = client.get("/api/data-status")
    assert r.status_code == 200
    assert r.json()["records_loaded"] > 0


def test_total_revenue():
    r = client.post("/api/ask", json={"question": "What is the total revenue?"})
    assert r.status_code == 200
    data = r.json()
    assert data["operation"] == "total_revenue"
    assert "total_revenue" in data["metrics"]
    assert data["metrics"]["total_revenue"] > 0


def test_highest_product():
    r = client.post("/api/ask", json={"question": "Which product generated the highest revenue?"})
    assert r.status_code == 200
    assert r.json()["operation"] == "highest_revenue_product"


def test_monthly():
    r = client.post("/api/ask", json={"question": "What is the monthly revenue trend?"})
    assert r.status_code == 200
    assert r.json()["operation"] == "monthly_revenue"
    assert len(r.json()["supporting_data"]) > 0


def test_top_region():
    r = client.post("/api/ask", json={"question": "Which region generated the highest sales?"})
    assert r.status_code == 200
    assert r.json()["operation"] == "top_region"


def test_compare_months():
    r = client.post("/api/ask", json={"question": "How did revenue change between January and February?"})
    assert r.status_code == 200
    d = r.json()
    assert d["operation"] == "compare_months"
    assert "percentage_change" in d["metrics"]


def test_unsupported():
    r = client.post("/api/ask", json={"question": "What is the weather?"})
    assert r.status_code == 200
    assert r.json()["operation"] == "unsupported"


def test_malformed():
    r = client.post("/api/ask", json={})
    assert r.status_code == 422


def test_zero_baseline():
    # direct function test
    from app.services.analytics_service import compare_months
    db = TestingSession()
    # monkey: ensure function handles zero; just call with nonexistent month returns None
    assert compare_months(db, "2026-99", "2026-01") is None
    db.close()
