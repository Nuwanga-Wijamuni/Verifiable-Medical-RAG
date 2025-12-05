import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "VitalSource RAG"
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    LLAMA_CLOUD_API_KEY: str = os.getenv("LLAMA_CLOUD_API_KEY")
    
    # Infrastructure
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"

    def __init__(self):
        # Validate critical keys for Phase 1
        if not self.LLAMA_CLOUD_API_KEY:
            print("⚠️  WARNING: LLAMA_CLOUD_API_KEY is missing. Ingestion will fail.")
            
        os.makedirs(self.RAW_DATA_DIR, exist_ok=True)
        os.makedirs(self.PROCESSED_DATA_DIR, exist_ok=True)

settings = Settings()