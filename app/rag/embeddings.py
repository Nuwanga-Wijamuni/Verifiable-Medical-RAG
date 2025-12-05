import google.generativeai as genai
from app.core.config import settings
from typing import List

# Configure SDK
if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)

def generate_embedding(text: str) -> List[float]:
    """
    Generates a vector embedding for a single text string using Gemini.
    """
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY missing.")
        
    # Model: models/text-embedding-004 is the latest stable
    model = 'models/text-embedding-004' 
    
    try:
        result = genai.embed_content(
            model=model,
            content=text,
            task_type="retrieval_document",
            title="Medical Record"
        )
        return result['embedding']
    except Exception as e:
        print(f"⚠️ Embedding failed: {e}")
        return []