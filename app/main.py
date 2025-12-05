from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Verifiable RAG for Medical Documents using LlamaParse and Weaviate.",
    version="1.0.0"
)

# CORS (Allow Frontend to talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "VitalSource API is running", 
        "docs": "/docs",
        "ingestion_endpoint": "/api/v1/ingest"
    }

if __name__ == "__main__":
    import uvicorn
    # Use the string import to avoid loop conflicts on Windows
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)