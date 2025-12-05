import os
import nest_asyncio
import re
from typing import List
from langchain_core.documents import Document
from llama_parse import LlamaParse
from app.core.config import settings

# Apply nest_asyncio to allow running async code in scripts/FastAPI
nest_asyncio.apply()

def extract_year_from_filename(filename: str) -> str:
    """Extracts year (e.g., 2023) from filename for metadata tagging."""
    match = re.search(r"202\d", filename)
    return str(match.group(0)) if match else "Unknown"

def clean_medical_text(text: str) -> str:
    """
    Removes common boilerplate noise from the report to improve retrieval quality.
    """
    # Remove specific headers/footers found in your samples
    noise_patterns = [
        "CLINICTECH LABS - COMPREHENSIVE REPORT",
        "123 Innovation Drive",
        "123 innovation Drive", # Handle typos
        "123 Innovation Dove",  # Handle OCR typos
        "Page [0-9]+",
        "--- PAGE [0-9]+ ---"
    ]
    
    cleaned_text = text
    for pattern in noise_patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)
    
    return cleaned_text.strip()

async def vision_based_parsing(file_paths: List[str]) -> List[Document]:
    """
    Ingestion using LlamaParse (State-of-the-Art for RAG).
    Async version to prevent Event Loop conflicts.
    """
    processed_documents = []

    if not file_paths:
        return []

    if not settings.LLAMA_CLOUD_API_KEY:
        raise ValueError("LLAMA_CLOUD_API_KEY is missing in .env")

    # Initialize the Parser
    # UPDATED: using 'user_prompt' instead of 'parsing_instruction'
    parser = LlamaParse(
        api_key=settings.LLAMA_CLOUD_API_KEY,
        result_type="markdown",
        verbose=True,
        language="en",
        user_prompt=(
            "This is a medical lab report. "
            "Ensure all numerical values, units (like mg/dL), and flags (H, L) are preserved exactly in the markdown tables. "
            "Do not merge separate tests into one row. "
            "Keep the exact table structure with headers."
        )
    )

    print(f"🚀 Initialized LlamaParse. Processing {len(file_paths)} files...")

    for pdf_path in file_paths:
        filename = os.path.basename(pdf_path)
        print(f"\n📄 Sending to LlamaCloud: {filename}")
        
        try:
            # UPDATED: Use async load (aload_data)
            parsed_docs = await parser.aload_data(pdf_path)
            year = extract_year_from_filename(filename)

            for i, doc in enumerate(parsed_docs):
                page_num = i + 1
                
                # 1. Clean the text (Remove noise)
                cleaned_content = clean_medical_text(doc.text)
                
                # 2. Convert to LangChain Document with rich metadata
                langchain_doc = Document(
                    page_content=cleaned_content,
                    metadata={
                        "source": filename,
                        "page": page_num,
                        "year": int(year) if year != "Unknown" else None,
                        "extraction_method": "llama_parse_ocr_medical"
                    }
                )
                processed_documents.append(langchain_doc)
                
                # Debug: Save processed markdown
                debug_path = settings.PROCESSED_DATA_DIR / f"{filename}_p{page_num}.md"
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_content)
                
            print(f"   ✅ Successfully parsed {len(parsed_docs)} pages.")

        except Exception as e:
            print(f"   ❌ Error parsing {filename}: {e}")

    return processed_documents