from app.core.config import settings
import weaviate

def get_weaviate_client():
    """
    Returns a Weaviate client instance.
    """
    # Note: Weaveite client connection is synchronous, designed for use with FastAPI Depends
    client = weaviate.Client(
        url=settings.WEAVIATE_URL,
        additional_headers={
            # Removed the problematic "X-OpenAI-Api-Key" header check
            "X-Google-Api-Key": settings.GOOGLE_API_KEY or "" # Pass Google Key if needed by Weaviate module
        }
    )
    return client