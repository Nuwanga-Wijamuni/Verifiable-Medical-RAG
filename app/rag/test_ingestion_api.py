import glob
import uvicorn
import os
import sys
from fastapi import FastAPI
from app.rag.ingestion import vision_based_parsing
from app.core.config import settings

# Add project root to sys path
sys.path.append(str(settings.BASE_DIR))

app = FastAPI(title="Phase 1: Extraction Inspector")

@app.get("/")
def health_check():
    return {"status": "Active", "message": "Go to /inspect-extraction to see raw LlamaParse output."}

@app.get("/inspect-extraction")
async def inspect_extraction():
    """
    1. Ingest (LlamaParse)
    2. Skip Chunking
    3. Return Full Markdown
    """
    pdf_pattern = str(settings.RAW_DATA_DIR / "*.pdf")
    files = glob.glob(pdf_pattern)

    if not files:
        return {"error": "No PDFs found! Please put files in data/raw/"}

    print(f"🚀 Starting Extraction for {len(files)} files...")
    
    # Run the Async Ingestion
    raw_docs = await vision_based_parsing(files)
    
    # Format output for browser
    results = []
    for doc in raw_docs:
        results.append({
            "metadata": doc.metadata,
            "full_content": doc.page_content  # Show EVERYTHING
        })

    return {
        "status": "Success",
        "total_pages": len(raw_docs),
        "documents": results
    }

if __name__ == "__main__":
    print("📢 Server starting at http://127.0.0.1:8000")
    uvicorn.run("app.rag.test_ingestion_api:app", host="127.0.0.1", port=8000, reload=True)