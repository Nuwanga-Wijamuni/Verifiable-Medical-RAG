import os
import shutil
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.api.schemas import InspectionResponse, ExtractedDocument, QueryRequest, QueryResponse # <- IMPORT FIX
from app.core.config import settings
from app.rag.ingestion import vision_based_parsing
# NOTE: We skip chunking imports/calls for this inspection phase.
# from app.rag.chunking import chunk_medical_documents 

router = APIRouter()

@router.post("/ingest", response_model=InspectionResponse)
async def ingest_documents(files: List[UploadFile] = File(...)):
    """
    STEP 1: EXTRACTION INSPECTION ONLY
    This endpoint runs LlamaParse and returns the raw extracted Markdown 
    to verify extraction quality.
    """
    saved_paths = []
    
    # 1. Save Files
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
            
        file_path = settings.RAW_DATA_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(str(file_path))
    
    if not saved_paths:
        raise HTTPException(status_code=400, detail="No PDF files uploaded")

    # 2. Extract (Vision Pipeline) - CRITICAL: AWAITED
    raw_docs = await vision_based_parsing(saved_paths)
    
    # 3. Format the response to show the content of the extracted documents
    
    response_data = []
    for doc in raw_docs:
        # Pydantic validation handles conversion errors here
        response_data.append(ExtractedDocument(
            source=doc.metadata.get('source', 'N/A'),
            page=doc.metadata.get('page', 0),
            year=doc.metadata.get('year'),
            extraction_method=doc.metadata.get('extraction_method', 'N/A'),
            content_preview=doc.page_content[:150] + "...", 
            full_content=doc.page_content
        ))
    
    return InspectionResponse(
        status="Extraction Complete (Chunking Skipped)",
        total_pages_extracted=len(raw_docs) if raw_docs else 0,
        extracted_documents=response_data
    )

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Stub for Phase 5 (Retrieval)
    """
    # This route is unchanged and uses the original schema definition
    return QueryResponse(
        answer="This is a placeholder answer until Phase 5 is implemented.",
        citations=[],
        confidence_score=0.0
    )