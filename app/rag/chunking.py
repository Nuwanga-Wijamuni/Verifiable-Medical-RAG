from typing import List, Dict, Any
import re
import uuid

# --- Custom Recursive Splitter (No LangChain) ---
def recursive_split_text(text: str, chunk_size: int = 1500, chunk_overlap: int = 150) -> List[str]:
    """
    Splits text into chunks of a specified size with overlap, 
    trying to break at logical separators like newlines.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        if end >= text_len:
            chunks.append(text[start:])
            break
        
        # Try to find a separator to split on (newline, period, space)
        # We search backwards from the 'end' point
        split_found = False
        for separator in ["\n\n", "\n", ". ", " "]:
            split_index = text.rfind(separator, start, end)
            if split_index != -1:
                # Found a good split point
                chunks.append(text[start:split_index])
                # Move start forward, minus overlap
                start = split_index + len(separator) - chunk_overlap
                split_found = True
                break
        
        if not split_found:
            # No separator found, force split at chunk_size
            chunks.append(text[start:end])
            start = end - chunk_overlap

    return chunks

def chunk_medical_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Splits medical markdown reports into logical sections (Chunks).
    
    Expected input: List of dicts [{'page_content': str, 'metadata': dict}]
    Returns: List of dicts
    """
    
    if not documents:
        print("⚠️ No documents provided to chunker.")
        return []

    final_chunks = []

    for doc in documents:
        content = doc.get("page_content", "")
        metadata = doc.get("metadata", {})
        
        if not content:
            continue
            
        # --- 1. Extract Global Context ---
        patient_match = re.search(r"PATIENT:\s*(.*?)(\n|$)", content)
        date_match = re.search(r"COLL DATE:\s*(.*?)(\n|$)", content)
        
        patient_context = patient_match.group(1).strip() if patient_match else "Unknown Patient"
        date_context = date_match.group(1).strip() if date_match else "Unknown Date"
        
        global_context_str = f"Patient: {patient_context} | Date: {date_context}\n"

        # --- 2. Split by Header (Custom Implementation) ---
        # We split the text by lines starting with #
        # This mimics MarkdownHeaderTextSplitter
        lines = content.split('\n')
        header_splits = []
        current_chunk_lines = []
        
        for line in lines:
            # If line starts with #, it's a new section
            if line.strip().startswith('#'):
                if current_chunk_lines:
                    header_splits.append("\n".join(current_chunk_lines))
                    current_chunk_lines = []
                current_chunk_lines.append(line)
            else:
                current_chunk_lines.append(line)
        
        if current_chunk_lines:
            header_splits.append("\n".join(current_chunk_lines))

        for split_content in header_splits:
            # Determine section tag
            header_line = split_content.split("\n")[0].lower()
            section_tag = "other"
            
            if any(x in header_line for x in ["blood count", "cbc"]): section_tag = "cbc"
            elif any(x in header_line for x in ["lipid", "cholesterol"]): section_tag = "lipid_profile"
            elif any(x in header_line for x in ["diabetes", "glucose", "hba1c"]): section_tag = "glucose_diabetes"
            elif any(x in header_line for x in ["kidney", "creatinine"]): section_tag = "kidney_function"
            elif any(x in header_line for x in ["liver", "sgpt", "sgot"]): section_tag = "liver_function"
            elif "electrolyte" in header_line: section_tag = "electrolytes"
            elif any(x in header_line for x in ["interpretation", "diagnosis"]): section_tag = "clinical_interpretation"

            # --- 3. Filter "Other" / Boilerplate ---
            if section_tag == "other" and len(split_content) < 500:
                continue

            # --- 4. Enhance Chunk with Context ---
            enhanced_content = global_context_str + split_content

            # Create metadata dict copy
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_id"] = str(uuid.uuid4())
            chunk_metadata["section"] = section_tag
            
            # --- 5. Recursive Fallback ---
            if len(enhanced_content) > 2000:
                # Use our custom recursive splitter
                sub_texts = recursive_split_text(enhanced_content, chunk_size=1500, chunk_overlap=150)
                for text in sub_texts:
                    sub_meta = chunk_metadata.copy()
                    sub_meta["chunk_id"] = str(uuid.uuid4())
                    final_chunks.append({
                        "page_content": text,
                        "metadata": sub_meta
                    })
            else:
                final_chunks.append({
                    "page_content": enhanced_content,
                    "metadata": chunk_metadata
                })

    print(f"✅ Chunking Complete. Created {len(final_chunks)} high-quality chunks.")
    return final_chunks