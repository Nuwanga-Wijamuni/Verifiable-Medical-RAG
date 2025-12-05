from pydantic import BaseModel, Field
from typing import List, Optional

class IngestionResponse(BaseModel):
    status: str
    message: str
    files_processed: List[str]
    total_pages: int
    total_chunks: int

class QueryRequest(BaseModel):
    question: str
    year_filter: Optional[int] = None

class Citation(BaseModel):
    source: str
    page: int
    year: Optional[int]
    snippet: str
    chunk_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence_score: Optional[float] = None