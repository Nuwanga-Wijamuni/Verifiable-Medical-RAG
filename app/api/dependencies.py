from app.core.config import settings
import weaviate

def get_weaviate_client():
    """
    Returns a Weaviate client instance.
    You can use this in your routes: client = Depends(get_weaviate_client)
    """
    # Assuming local Weaviate for now based on your assessment constraints
    # If using Weaviate Cloud, you'd add auth_client_secret here
    client = weaviate.Client(
        url=settings.WEAVIATE_URL, 
        additional_headers={
            "X-OpenAI-Api-Key": settings.OPENAI_API_KEY # If using OpenAI embeddings internally
        }
    )
    return client