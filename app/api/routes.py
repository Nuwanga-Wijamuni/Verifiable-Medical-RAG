import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.api.schemas import IngestionResponse, QueryRequest, QueryResponse, Citation
from app.core.config import settings
from app.rag.ingestion import vision_based_parsing
from app.rag.chunking import chunk_medical_documents
from app.rag.vector_store import add_chunks_to_weaviate

# --- NEW IMPORTS FOR PHASE 3 ---
from app.rag.retriever import get_relevant_chunks
from app.rag.generation import generate_answer_with_groq

router = APIRouter()

@router.post("/ingest", response_model=IngestionResponse)
async def ingest_documents(files: List[UploadFile] = File(...)):
    """
    PHASE 2: FULL INGESTION PIPELINE
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

    # 2. Extract (LlamaParse -> Dicts)
    # Note: raw_docs is now List[Dict]
    raw_docs = await vision_based_parsing(saved_paths)
    
    # 3. Chunk (Pure Python -> Dicts)
    chunks = chunk_medical_documents(raw_docs)
    
    if not chunks:
        raise HTTPException(status_code=400, detail="No text extracted from documents.")

    # 4. Index (Native Weaviate)
    try:
        add_chunks_to_weaviate(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing Error: {e}")
    
    return IngestionResponse(
        status="Success",
        message=f"Ingestion complete. {len(chunks)} chunks indexed.",
        files_processed=[os.path.basename(p) for p in saved_paths],
        total_pages=len(raw_docs),
        total_chunks=len(chunks)
    )

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    PHASE 3: RETRIEVAL & GENERATION (GROQ POWERED)
    """
    print(f"🔎 Searching for: {request.question} (Year Filter: {request.year_filter})")
    
    # 1. Retrieve (Uses your Finetuned Retriever)
    relevant_chunks = get_relevant_chunks(
        query=request.question,
        year=request.year_filter
    )
    
    if not relevant_chunks:
        return QueryResponse(
            answer="I couldn't find any medical records matching your query and year filter.",
            citations=[]
        )

    # 2. Generate (Uses Groq / Llama 3)
    print("🧠 Generating answer with Groq...")
    answer_text = generate_answer_with_groq(
        query=request.question, 
        chunks=relevant_chunks
    )

    # 3. Format Citations
    citations = []
    for chunk in relevant_chunks:
        citations.append(Citation(
            source=chunk.get("source", "Unknown"),
            page=chunk.get("page", 0),
            year=chunk.get("year"),
            chunk_id=chunk.get("chunk_id", "Unknown"), # <--- MAPPING ADDED
            snippet=chunk.get("content", "")[:200] + "..." # Preview
        ))

    return QueryResponse(
        answer=answer_text,
        citations=citations,
        confidence_score=1.0
    )