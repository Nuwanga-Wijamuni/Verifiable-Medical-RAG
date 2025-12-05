from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

def chunk_medical_documents(documents: List[Document]) -> List[Document]:
    """
    Splits medical markdown reports into logical sections (Chunks).
    Strategy: 
    1. Split by Markdown Headers (# Section) to keep tables intact.
    2. If a section is still too big, split recursively safely.
    """
    
    # Safety Check: If input is None or empty, return empty list immediately
    if not documents:
        print("⚠️ No documents provided to chunker.")
        return []

    # 1. Define Headers to Split On
    # LlamaParse generates # for main titles and ## for subsections like "1. COMPLETE BLOOD COUNT"
    headers_to_split_on = [
        ("#", "Report Section"),      # e.g., "1. COMPLETE BLOOD COUNT"
        ("##", "Sub-Section"),        # e.g., "TEST NAME"
        ("###", "Detail"),
    ]

    # This splitter respects the structure LlamaParse created
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, 
        strip_headers=False # Keep headers so context is preserved
    )

    final_chunks = []

    for doc in documents:
        if not doc.page_content:
            continue
            
        # A. Split by Header (Logical Chunks)
        # This keeps the "Lipid Profile" table together
        header_splits = markdown_splitter.split_text(doc.page_content)
        
        # B. Safety Split (Recursive)
        # If a single table is huge (>2000 chars), we split it safely to fit in vector limits
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        for split in header_splits:
            # Transfer Metadata (Year, Source) from the parent doc to the new chunk
            split.metadata.update(doc.metadata)
            
            # Ensure chunk isn't too massive
            if len(split.page_content) > 2500:
                sub_chunks = text_splitter.split_documents([split])
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(split)

    print(f"✅ Chunking Complete. Created {len(final_chunks)} granular chunks from {len(documents)} pages.")
    
    # CRITICAL FIX: Ensure we return the list, never None
    return final_chunks