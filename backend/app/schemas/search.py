from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Any, Dict, Optional, List
from datetime import datetime


class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10


class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    score: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    meta_data: Dict[str, Any]


class SearchHistoryResponse(BaseModel):
    # Enable reading from ORM attributes
    model_config = ConfigDict(from_attributes=True)

    id: int
    query: str
    results: Dict[str, Any]
    # Read from ORM attribute "metadata", expose as "metadata" in JSON
    meta_data: Optional[Dict[str, Any]] = Field(default=None, alias="meta_data")
    created_at: datetime
