#scripts/seed_databse.py
import json
import hashlib
import os
import sys
import pathlib
from collections import Counter
from dotenv import load_dotenv

# --- Boilerplate to set up path for imports ---
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# --- End Boilerplate ---

from interview_system.services.vector_store import get_vector_store

INPUT_FILE = "questions.txt"

def process_questions(questions: list) -> list:
    """
    Transforms questions and reports duplicates without removing them.
    1. Transforms 'id', 'domain', and 'rubric_id' for all questions.
    2. Detects duplicates based on 'text' and prints a warning with the hash ID.
    """
    transformed_questions = []
    
    print("--- Checking for duplicate question texts ---")
    text_counts = Counter(q.get("text", "") for q in questions)
    duplicates_found = False
    for text, count in text_counts.items():
        if count > 1:
            duplicates_found = True
            duplicate_id = hashlib.sha256(text.encode("utf-8")).hexdigest()
            print(f"\nWARNING: Duplicate question found ({count} times). Please manually review and delete from questions.txt.")
            print(f"  - Generated ID: {duplicate_id}")
            
            # --- FIXED SECTION ---
            # Prepare the text on a separate line to avoid complex f-string issues.
            cleaned_text = text[:80].replace("\n", " ")
            print(f'  - Text: "{cleaned_text}..."')
            # --- END FIXED SECTION ---
    
    if not duplicates_found:
        print("No duplicate question texts found.")

    # Second, transform all questions for upserting
    for q in questions:
        original_id = q.get("id", "")
        original_domain = q.get("domain", "")
        question_text = q.get("text", "")

        new_id = hashlib.sha256(question_text.encode("utf-8")).hexdigest()

        new_domain = original_domain
        if original_id.startswith("q-") and original_id.count("-") >= 2:
            parts = original_id.split("-")
            topic = "-".join(parts[1:-1])
            if topic:
                new_domain = f"{original_domain}-{topic}"
        
        if q.get("rubric_id") is None:
            q["rubric_id"] = ""

        q["id"] = new_id
        q["domain"] = new_domain
        transformed_questions.append(q)
        
    return transformed_questions

def main():
    """
    Main function to read, process, report duplicates, and upsert questions.
    """
    load_dotenv()
    if not all(os.getenv(k) for k in ["GOOGLE_API_KEY", "PINECONE_API_KEY"]):
        print("Error: GOOGLE_API_KEY and PINECONE_API_KEY must be set in .env file.")
        return

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            questions_data = json.load(f)
        print(f"Loaded {len(questions_data)} questions from {INPUT_FILE}.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {INPUT_FILE}: {e}")
        return

    questions_to_upsert = process_questions(questions_data)

    print("\n--- Connecting to vector store and upserting data ---")
    store = get_vector_store()
    store.upsert_questions(questions_to_upsert)
    print(f"\nSuccessfully sent {len(questions_to_upsert)} records for upserting to Pinecone.")
    print("Note: The final record count in Pinecone may be lower if duplicates were not removed.")

if __name__ == "__main__":
    main()