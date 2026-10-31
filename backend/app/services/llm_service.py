import json
import urllib.request
import urllib.error

from app.config import LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_BASE_URL


def _call_openai(question: str, result_summary: str) -> str:
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful BI assistant. Explain the provided verified result in one or two sentences. Do not change numbers."},
            {"role": "user", "content": f"Question: {question}\nVerified result: {result_summary}"},
        ],
        "temperature": 0.2,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{LLM_BASE_URL}/chat/completions",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {LLM_API_KEY}"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read())
    return body["choices"][0]["message"]["content"].strip()


def explain(question: str, result_summary: str):
    if LLM_PROVIDER in ("openai", "openai-compatible") and LLM_API_KEY:
        try:
            text = _call_openai(question, result_summary)
            return text, True, LLM_PROVIDER
        except Exception:
            pass
    # deterministic fallback
    return f"Based on verified database calculations: {result_summary}", False, "deterministic_fallback"
