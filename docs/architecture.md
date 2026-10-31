# Architecture

Modular monolith. FastAPI backend, React/Vite frontend, SQLite DB.

Data flow: CSV -> data_loader validation -> SQLite -> analytics_service deterministic queries -> question_parser maps NL to allowlisted ops -> API -> frontend.

AI: llm_service abstraction; deterministic fallback when no key. LLM only explains verified results.
