import os
from groq import Groq
from typing import List, Dict, Any
from app.core.config import settings

# Initialize Groq Client
client = Groq(
    api_key=settings.GROQ_API_KEY,
)

def format_context_for_llm(chunks: List[Dict[str, Any]]) -> str:
    """Formats retrieved chunks into a structured string for the LLM."""
    formatted_text = ""
    for i, chunk in enumerate(chunks):
        formatted_text += f"""
--- SOURCE {i+1} ---
Document: {chunk.get('source')}
Date/Year: {chunk.get('year')}
Section: {chunk.get('section')}
Content:
{chunk.get('content')}
-------------------
"""
    return formatted_text

def generate_answer_with_groq(query: str, chunks: List[Dict[str, Any]]) -> str:
    """
    Generates a medical answer using Llama 3.3 via Groq.
    """
    if not chunks:
        return "I could not find any relevant medical records to answer your question."

    context = format_context_for_llm(chunks)
    
    # System Prompt: Enforces strict "Verifiable RAG" behavior
    system_prompt = """
    You are a Clinical AI Assistant. Your goal is to answer questions based ONLY on the provided medical context.
    
    STRICT RULES:
    1. GROUNDING: Answer strictly using the 'Context' provided below. If the answer is not in the text, say "Information not found in the records."
    2. CITATIONS: When you mention a specific value (e.g., "Hemoglobin 14.5"), immediately cite the source ID like this: [Source 1].
    3. ACCURACY: Do not interpret or calculate unless explicitly asked. Copy units exactly (mg/dL, mmol/L).
    4. TONE: Professional, clinical, and direct.
    
    Context:
    {context}
    """

    user_message = f"User Question: {query}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt.format(context=context)
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            # UPDATED MODEL NAME
            model="openai/gpt-oss-120b",
            temperature=0, 
            max_tokens=500,
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"❌ Groq Generation Error: {e}")
        return f"Error generating answer: {str(e)}"