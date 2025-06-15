from typing import Dict, List, Any

def create_system_prompt(rag_data: Dict[str, List[Any]]) -> str:
    """
    Builds a dynamic system prompt for the Gemini model using processed RAG data.
    """
    
    # --- Format each data category into a string ---

    # General Info and Contacts
    info_pieces = []
    for item in rag_data.get("general_info", []) + rag_data.get("contact_info", []) + rag_data.get("announcements", []):
        info_pieces.append(f"- {item.get('title', '')}: {item.get('text_content', '')}")
    general_info_str = "\n".join(info_pieces) if info_pieces else "No general information available."

    # Courses (Grouped by Department)
    courses_by_dept = {}
    for course in rag_data.get("courses", []):
        dept = course.get("metadata", {}).get("department", "Uncategorized")
        if dept not in courses_by_dept:
            courses_by_dept[dept] = []
        courses_by_dept[dept].append(course.get('text_content', ''))
    
    course_str_parts = []
    for dept, courses in courses_by_dept.items():
        course_str_parts.append(f"\nDepartment: {dept}\n" + "\n".join([f"  - {c}" for c in courses]))
    courses_str = "\n".join(course_str_parts) if course_str_parts else "No specific course listings available. You can mention the available departments."

    # Departments
    department_names = [d.get("metadata", {}).get("department") for d in rag_data.get("departments", [])]
    departments_str = ", ".join(filter(None, department_names)) if department_names else "No departments listed."

    # FAQs
    faqs_str_parts = []
    for faq in rag_data.get("faqs", []):
        faqs_str_parts.append(f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}")
    faqs_str = "\n\n".join(faqs_str_parts) if faqs_str_parts else "No frequently asked questions available."

    # --- Assemble the final prompt ---

    system_prompt = f"""
You are RNVP Bot, a helpful and friendly customer service assistant for the Rift Valley National Polytechnic (RVNP).
Your primary goal is to answer user questions accurately based *ONLY* on the information provided below.
Do not make up information. If the answer is not in the provided text, state that you don't have that information.
Be concise and clear in your answers.

--- AVAILABLE INFORMATION ---

[General Information, Contacts, and Announcements]
{general_info_str}

[Available Departments]
{departments_str}

[Course Listings by Department]
{courses_str}

[Frequently Asked Questions about Higher Education Funding]
{faqs_str}

--- END OF INFORMATION ---

Instructions:
1.  Carefully read the user's question.
2.  Find the most relevant section(s) in the "AVAILABLE INFORMATION" above.
3.  Construct your answer using only the provided text.
4.  If a user asks about something not covered (e.g., specific exam dates, library hours), politely state that you do not have that specific information.
5.  When asked about admissions, use the information from the "Announcements" or "General Information" sections.
"""
    return system_prompt