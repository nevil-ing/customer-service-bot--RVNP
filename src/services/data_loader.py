import os
import json
from typing import Dict, List, Any

# Build the absolute path to the dataset directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_FILE = os.path.join(BASE_DIR, "dataset", "combined_rag_data.jsonl")

def load_and_process_rag_data() -> Dict[str, List[Any]]:
    """
    Loads and processes the combined RAG data from the JSONL file.

    Returns:
        A dictionary with categorized data.
    """
    categorized_data = {
        "general_info": [],
        "contact_info": [],
        "announcements": [],
        "courses": [],
        "departments": [],
        "faqs": []
    }

    if not os.path.exists(DATASET_FILE):
        print(f"Warning: Data file not found at {DATASET_FILE}. Prompt will be basic.")
        return categorized_data

    with open(DATASET_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line)
                
                # Handle RVIST data
                content_type = record.get("content_type")
                if content_type == "general_info":
                    categorized_data["general_info"].append(record)
                elif content_type == "contact_info":
                    categorized_data["contact_info"].append(record)
                elif content_type == "announcement":
                    categorized_data["announcements"].append(record)
                elif content_type == "course_info":
                    categorized_data["courses"].append(record)
                elif content_type == "department_page_no_courses_itemized":
                     categorized_data["departments"].append(record)

                # Handle HEF data (which has a nested faq_list)
                if "faq_list" in record and isinstance(record["faq_list"], list):
                    categorized_data["faqs"].extend(record["faq_list"])

            except json.JSONDecodeError:
                print(f"Warning: Skipping malformed line in {DATASET_FILE}")
                continue
    
    # Deduplicate FAQs based on the question
    unique_faqs = {item['question'].strip(): item for item in categorized_data['faqs']}.values()
    categorized_data['faqs'] = list(unique_faqs)
    
    return categorized_data