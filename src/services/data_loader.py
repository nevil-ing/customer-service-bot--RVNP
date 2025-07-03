import os
import json
from typing import Dict, List, Any


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

                
                if "faq_list" in record and isinstance(record["faq_list"], list):
                    categorized_data["faqs"].extend(record["faq_list"])
                    
                elif content_type == "courses_detailed":
                        categorized_data["courses_detailed"] = record.get("data", [])
                elif content_type == "fees_structure":
                        categorized_data["fees_structure"] = record  

            except json.JSONDecodeError:
                print(f"Warning: Skipping malformed line in {DATASET_FILE}")
                continue
    
    
    unique_faqs = {item['question'].strip(): item for item in categorized_data['faqs']}.values()
    categorized_data['faqs'] = list(unique_faqs)
    
    return categorized_data