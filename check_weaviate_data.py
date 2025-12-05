import weaviate
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_data():
    print("🕵️ Connecting to Weaviate at http://localhost:8080...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY is missing from .env file.")
        return

    try:
        # Connect to local Weaviate
        client = weaviate.Client(
            url="http://localhost:8080",
            additional_headers={
                "X-Google-Api-Key": api_key
            }
        )
        
        if not client.is_ready():
             print("❌ Weaviate is not ready. Is the Docker container running?")
             return
             
        print("✅ Connected to Weaviate!")

    except Exception as e:
        print(f"❌ Failed to connect to Weaviate: {e}")
        return

    # 1. Check Schema
    try:
        schema = client.schema.get()
        classes = [cls['class'] for cls in schema.get('classes', [])]
        print(f"\n📋 Current Schema Classes found: {classes}")
        
        if "MedicalRecord" not in classes:
             print("⚠️ WARNING: Class 'MedicalRecord' not found in schema. Did ingestion run successfully?")
             return
             
    except Exception as e:
        print(f"❌ Failed to fetch schema: {e}")
        return

    # 2. Check Object Count
    try:
        # Simple GraphQL count query
        result = client.query.aggregate("MedicalRecord").with_meta_count().do()
        if 'errors' in result:
             print(f"❌ Error counting objects: {result['errors']}")
        else:
             total_objects = result['data']['Aggregate']['MedicalRecord'][0]['meta']['count']
             print(f"\n✅ Total Objects in 'MedicalRecord': {total_objects}")
             
             if total_objects == 0:
                 print("⚠️ The class exists but is empty. No data was indexed.")
                 return
    except Exception as e:
        print(f"❌ Error counting objects: {e}")
        return

    # 3. Fetch and Print Samples
    print("\n📝 Fetching top 3 stored chunks...")
    try:
        result = (
            client.query
            .get("MedicalRecord", ["content", "source", "year", "section"])
            .with_limit(3)
            .do()
        )

        if 'errors' in result:
            print(f"❌ Query error: {result['errors']}")
            return

        objects = result['data']['Get']['MedicalRecord']
        
        if not objects:
            print("⚠️ No objects returned from query.")
        
        for i, obj in enumerate(objects):
            print(f"\n--- Chunk {i+1} ---")
            # Use json.dumps for pretty printing the dictionary parts if needed, 
            # or just clean formatting as below
            print(f"📂 Source:  {obj.get('source')}")
            print(f"📅 Year:    {obj.get('year')}")
            print(f"🏷️ Section: {obj.get('section')}")
            
            content = obj.get('content', '')
            # Replace newlines to make the preview cleaner
            content_preview = content[:150].replace('\n', ' ')
            print(f"📄 Content: {content_preview}...") 
            
    except Exception as e:
        print(f"❌ Error fetching samples: {e}")

if __name__ == "__main__":
    check_data()