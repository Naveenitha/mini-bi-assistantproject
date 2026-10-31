from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class DataStatus(BaseModel):
    records_loaded: int
    records_excluded: int
    exclusion_reasons: Dict[str, int]
    source_file: str


class AskResponse(BaseModel):
    question: str
    operation: str
    answer: str
    metrics: Dict[str, Any] = {}
    supporting_data: List[Dict[str, Any]] = []
    data_quality: Dict[str, Any] = {}
    ai: Dict[str, Any] = {}
