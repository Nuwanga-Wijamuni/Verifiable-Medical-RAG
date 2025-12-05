from pydantic import BaseModel, Field # <-- CRITICAL: BaseModel imported here
from typing import List, Optional, Dict, Any

# --- Ingestion Schemas ---
class IngestionResponse(BaseModel):
    status: str
    message: str
    files_processed: List[str]
    total_pages: int
    total_chunks: int

# --- Inspection Schema (Temporary for Inspection phase) ---
# Used for the initial /ingest endpoint response
class ExtractedDocument(BaseModel):
    source: str
    page: int
    year: Optional[int]
    extraction_method: str
    content_preview: str
    full_content: str

class InspectionResponse(BaseModel):
    status: str
    total_pages_extracted: int
    extracted_documents: List[ExtractedDocument]


# --- Query/Retrieval Schemas (Placeholder for Phase 5) ---
class QueryRequest(BaseModel):
    question: str = Field(..., description="The clinical question to ask", example="What was my LDL level in 2023?")
    year_filter: Optional[int] = Field(None, description="Optional year to filter results", example=2023)

class Citation(BaseModel):
    source: str
    page: int
    year: Optional[int]
    snippet: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence_score: Optional[float] = None