# Mini AI Business Intelligence Assistant

## Overview
FastAPI backend + React/Vite frontend + SQLite. Answers 5 sales analytics questions from CSV.

## Setup Backend
```
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```
Load data:
```
curl -X POST http://localhost:8000/api/load-data
```

## Setup Frontend
```
cd frontend
npm install
cp .env.example .env
npm run dev
```
Open http://localhost:5173

## Tests
```
cd backend
python -m pytest -q
```

## Data Policy
Revenue = quantity * unit_price - discount for Completed only. Missing/invalid excluded and counted.

## API
GET /health, GET /api/data-status, POST /api/ask, POST /api/load-data

## What we built (step by step)
1. Inspected company CSV and assessment doc.
2. Designed modular monolith: config, database, models, services, routes.
3. Data loader validates columns, types, missing/invalid/duplicate/returned records; stores valid completed transactions in SQLite.
4. Analytics service computes total revenue, top product, monthly trend, top region, month comparison deterministically.
5. Question parser maps natural language to allowlisted operations; no arbitrary SQL.
6. LLM service abstraction with deterministic fallback; LLM only explains verified results.
7. FastAPI routes with Pydantic validation and error handling.
8. React/Vite frontend with loading/error/empty states and example questions.
9. Pytest tests for all operations, unsupported, malformed, edge cases.
10. Docs: README, architecture, AI report.
