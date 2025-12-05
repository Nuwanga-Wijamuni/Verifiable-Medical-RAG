import requests
import time
import re

# Configuration
API_URL = "http://localhost:8000/api/v1/query"

# Mixed Ground Truth Data (Spanning 2021, 2022, 2023)
test_cases = [
    # --- 2021 Data ---
    {
        "year": 2021,
        "question": "What is the patient's Hemoglobin level?",
        "expected_value": "14.5",
        "unit": "g/dL"
    },
    {
        "year": 2021,
        "question": "What is the Fasting Glucose result?",
        "expected_value": "85",
        "unit": "mg/dL"
    },
    
    # --- 2022 Data ---
    {
        "year": 2022,
        "question": "What is the Total Cholesterol level?",
        "expected_value": "215",
        "unit": "mg/dL"
    },
    {
        "year": 2022,
        "question": "What is the Creatinine level?",
        "expected_value": "0.95",
        "unit": "mg/dL"
    },
    {
        "year": 2022,
        "question": "What is the Triglycerides level?",
        "expected_value": "160",
        "unit": "mg/dL"
    },

    # --- 2023 Data ---
    {
        "year": 2023,
        "question": "What is the HbA1c level?",
        "expected_value": "7.1",
        "unit": "%"
    },
    {
        "year": 2023,
        "question": "What is the LDL Cholesterol result?",
        "expected_value": "155",
        "unit": "mg/dL"
    },
    {
        "year": 2023,
        "question": "What is the ALT (Liver Enzyme) level?",
        "expected_value": "65",
        "unit": "U/L"
    },
    {
        "year": 2023,
        "question": "What is the eGFR value?",
        "expected_value": "85",
        "unit": "mL/min"
    },
    {
        "year": 2023,
        "question": "What is the primary diagnosis mentioned in the interpretation?",
        "expected_value": "Type 2 Diabetes",
        "unit": "(Text Match)"
    }
]

def clean_text(text):
    """
    Normalizes text by removing markdown bolding (**), 
    converting to lowercase, and collapsing whitespace.
    """
    if not text: return ""
    # Remove Markdown bolding
    text = text.replace("**", "")
    # Replace non-breaking spaces with standard space
    text = text.replace("\u00a0", " ").replace("\u202f", " ")
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def run_evaluation():
    print(f"🧪 Starting Mixed Evaluation (10 Questions)...\n")
    score = 0
    
    for i, test in enumerate(test_cases):
        print(f"Test {i+1} ({test['year']}): {test['question']}")
        
        payload = {
            "question": test['question'],
            "year_filter": test['year']
        }
        
        try:
            start_time = time.time()
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            elapsed = time.time() - start_time
            
            answer = data.get("answer", "").strip()
            citations = data.get("citations", [])
            
            # Print Comparison for visual debug
            print(f"     🎯 Expected: {test['expected_value']} {test['unit']}")
            print(f"     🤖 AI Answer: {answer}")

            # ROBUST CHECK: Clean both strings before comparing
            clean_answer = clean_text(answer)
            clean_expected = clean_text(test['expected_value'])

            if clean_expected in clean_answer:
                print(f"  ✅ PASS ({elapsed:.2f}s)")
                score += 1
            else:
                print(f"  ❌ FAIL")
                
            # Verify Citations AND Print Chunk IDs
            if citations:
                cit = citations[0]
                cited_year = cit.get('year')
                chunk_id = cit.get('chunk_id', 'N/A') # <--- Get the ID
                
                # Allow int vs str comparison safety
                if str(cited_year) == str(test['year']):
                    print(f"     🔗 Verified Citation: Source {cited_year}")
                    print(f"        🆔 Chunk ID: {chunk_id}") # <--- Print the ID
                else:
                    print(f"     ⚠️ WRONG SOURCE YEAR: Got {cited_year}, Expected {test['year']}")
            else:
                print(f"     ⚠️ No citations provided!")

        except Exception as e:
            print(f"  ❌ ERROR: {e}")
        
        print("-" * 50)

    print(f"\n🏆 Final Score: {score}/{len(test_cases)}")
    if score == len(test_cases):
        print("🚀 VERIFICATION SUCCESSFUL: System correctly handled all mixed years.")
    else:
        print("⚠️ SYSTEM NEEDS TUNING.")

if __name__ == "__main__":
    run_evaluation()