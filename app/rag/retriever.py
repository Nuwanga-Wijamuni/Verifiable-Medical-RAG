from typing import List, Dict, Any, Optional
from app.api.dependencies import get_weaviate_client
from app.rag.embeddings import generate_embedding
from app.rag.vector_store import WEAVIATE_CLASS_NAME

def get_relevant_chunks(query: str, limit: int = 5, year: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retrieves relevant chunks from Weaviate using Semantic Search + Strict Metadata Filtering.
    """
    client = get_weaviate_client()
    
    # 1. Embed the User's Query (Using Google Gemini)
    # This must match the model used during ingestion.
    query_vector = generate_embedding(query)
    
    if not query_vector:
        print("⚠️ Failed to generate embedding for query.")
        return []

    # 2. Initialize the Weaviate Query Builder
    # CRITICAL UPDATE: We now fetch 'chunk_id' alongside other metadata
    query_builder = (
        client.query
        .get(WEAVIATE_CLASS_NAME, ["content", "source", "page", "year", "section", "chunk_id"])
        .with_near_vector({
            "vector": query_vector,
            "certainty": 0.60  # Threshold: Filters out irrelevant noise
        })
        .with_limit(limit)
    )

    # 3. Apply Strict Year Filter (Hard Filtering)
    # If a year is provided, we force Weaviate to ONLY look at that year.
    if year:
        year_filter = {
            "path": ["year"],
            "operator": "Equal",
            "valueInt": year
        }
        query_builder = query_builder.with_where(year_filter)

    # 4. Execute Query
    try:
        result = query_builder.do()
        
        # Safe extraction of results from the Weaviate GraphQL response
        if "data" in result and "Get" in result["data"]:
            chunks = result["data"]["Get"].get(WEAVIATE_CLASS_NAME, [])
        else:
            chunks = []
        
        if not chunks:
            # Debug log to help if retrieval fails
            print(f"⚠️ No chunks found for query: '{query}' with year filter: {year}")
            return []

        # 5. Optimization: Python-side Re-ranking
        # Weaviate finds "concepts", but sometimes we want to prioritize chunks 
        # that explicitly contain the exact keyword (e.g., "Creatinine").
        query_lower = query.lower()
        chunks.sort(key=lambda x: query_lower in x.get("content", "").lower(), reverse=True)
        
        return chunks

    except Exception as e:
        print(f"❌ Retrieval Error: {e}")
        return []