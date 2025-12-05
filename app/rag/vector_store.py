import weaviate
import time
from typing import List, Dict, Any
from app.api.dependencies import get_weaviate_client
from app.rag.embeddings import generate_embedding  # Or generate_embeddings_batch if you added it

WEAVIATE_CLASS_NAME = "MedicalRecord"

def wait_for_weaviate(client: weaviate.Client, timeout=30):
    print("⏳ Waiting for Weaviate to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            if client.is_ready(): 
                return True
        except: 
            pass
        time.sleep(1)
    return False

def create_schema_if_not_exists(client: weaviate.Client):
    try:
        schema = client.schema.get()
        classes = [c["class"] for c in schema.get("classes", [])]
        
        if WEAVIATE_CLASS_NAME in classes:
            client.schema.delete_class(WEAVIATE_CLASS_NAME)
            print(f"🧹 Deleted existing schema '{WEAVIATE_CLASS_NAME}'.")

        print(f"💾 Creating Schema '{WEAVIATE_CLASS_NAME}'...")
        
        class_obj = {
            "class": WEAVIATE_CLASS_NAME,
            "description": "Medical Report Chunks",
            "vectorizer": "none", 
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "source", "dataType": ["text"]},
                {"name": "page", "dataType": ["int"]},
                {"name": "year", "dataType": ["int"]},
                {"name": "section", "dataType": ["text"]},
                {"name": "chunk_id", "dataType": ["text"]}
            ]
        }
        
        client.schema.create_class(class_obj)
        print("✅ Schema created.")
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        raise e

def add_chunks_to_weaviate(chunks: List[Dict[str, Any]]):
    client = get_weaviate_client()
    
    if not wait_for_weaviate(client):
        raise ConnectionError("Weaviate unreachable")
        
    create_schema_if_not_exists(client)
    
    print(f"🚀 Generating embeddings & Indexing {len(chunks)} chunks...")
    
    with client.batch as batch:
        batch.batch_size = 100
        
        for chunk in chunks:
            # --- FIX STARTS HERE ---
            # 1. Handle structure: {'page_content': '...', 'metadata': {...}}
            text_content = chunk.get("page_content")
            metadata = chunk.get("metadata", {})
            
            if not text_content:
                print(f"⚠️ Skipping invalid chunk structure: {chunk.keys()}")
                continue

            # 2. Generate Vector
            vector = generate_embedding(text_content)
            
            if not vector:
                print(f"⚠️ Skipping chunk (No embedding)")
                continue
            
            # 3. Flatten metadata for Weaviate
            properties = {
                "content": text_content,
                "source": metadata.get("source", "Unknown"),
                "page": int(metadata.get("page", 0)),
                "year": int(metadata.get("year", 0)) if metadata.get("year") else 0,
                "section": metadata.get("section", "General"),
                "chunk_id": metadata.get("chunk_id", "unknown")
            }
            # --- FIX ENDS HERE ---
            
            batch.add_data_object(
                data_object=properties,
                class_name=WEAVIATE_CLASS_NAME,
                vector=vector 
            )
            
    print(f"✅ Successfully indexed {len(chunks)} chunks.")