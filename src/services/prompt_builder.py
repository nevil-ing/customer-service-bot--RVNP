
from typing import Dict, List, Any

def create_system_prompt(rag_data: Dict[str, List[Any]]) -> str:
    """
    Builds a dynamic and highly detailed system prompt using all available RAG data.
    """
    
   

    # General Info, Contacts, Announcement
    info_pieces = []
    for item in rag_data.get("general_info", []) + rag_data.get("contact_info", []) + rag_data.get("announcements", []):
        info_pieces.append(f"- {item.get('title', '')}: {item.get('text_content', '')}")
    general_info_str = "\n".join(info_pieces) if info_pieces else "No general information available."

    # course data
    detailed_course_parts = []
    for dept_data in rag_data.get("courses_detailed", []):
        dept_name = dept_data.get('department', 'Unknown Department')
        detailed_course_parts.append(f"\n### {dept_name}\n")
        detailed_course_parts.append("| Course Name | Level | Duration | Requirements |")
        detailed_course_parts.append("|---|---|---|---|")
        for course in dept_data.get('courses', []):
            level = course.get('level') if course.get('level') is not None else 'N/A'
            detailed_course_parts.append(f"| {course.get('curricula', '')} | {level} | {course.get('duration', '')} | {course.get('requirements', '')} |")
    detailed_courses_str = "\n".join(detailed_course_parts) if detailed_course_parts else "No detailed course list available."

   # fee data
    fees_data = rag_data.get("fees_structure")
    fee_parts = []
    if fees_data:
        fee_parts.append(f"### {fees_data.get('title', 'Fee Structure')}\n")
        
        fee_parts.append("**Annual Fees (Per Academic Year):**")
        for item in fees_data.get("annual_fees", []):
            fee_parts.append(f"- {item.get('item')}: {item.get('cost'):,.2f} KES")
        
        fee_parts.append("\n**One-Time Fees for New Students:**")
        for level, fees in fees_data.get("new_student_fees", {}).items():
            fee_parts.append(f"- **For {level.replace('_', ' ').title()}:** Total {fees.get('total'):,.2f} KES (Registration: {fees.get('registration'):,.2f}, Student ID: {fees.get('student_id'):,.2f}, Student Union: {fees.get('student_union'):,.2f})")

        fee_parts.append("\n**Important Notes on Fees:**")
        for note in fees_data.get("payment_instructions", []):
            fee_parts.append(f"- {note}")
    fees_str = "\n".join(fee_parts) if fee_parts else "No detailed fee structure available."

    # FAQs 
    faqs_str_parts = []
    for faq in rag_data.get("faqs", []):
        faqs_str_parts.append(f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}")
    faqs_str = "\n\n".join(faqs_str_parts) if faqs_str_parts else "No frequently asked questions available."


    system_prompt = f"""
You are "RNVP Bot," a professional and friendly Student Assistant for the Rift Valley National Polytechnic (RVNP). Your role is to provide accurate and clear information to prospective and current students.

# Your Persona:
- You are helpful, patient, and precise.
- You MUST act like a human representative. NEVER mention that you are an AI or refer to the text below as "provided information" or "knowledge base."
- Answer questions directly and conversationally. Use formatting like bullet points or bold text to improve readability.

# Core Knowledge:
You have access to official documents. Prioritize information from these sections for the highest accuracy.

--- OFFICIAL DOCUMENT DATA ---

[RVNP - Detailed Course List and Requirements (from official document)]
This is the primary source for all course-related questions.
{detailed_courses_str}

[RVNP - Fee Structure (Effective Sept 2024 Intake)]
This is the primary source for all fee-related questions.
{fees_str}

--- END OF OFFICIAL DOCUMENT DATA ---


--- GENERAL WEBSITE & FAQ DATA ---

[General Information, Contacts, and Announcements (from website)]
{general_info_str}

[Frequently Asked Questions about Higher Education Funding (from website)]
{faqs_str}

--- END OF GENERAL DATA ---

# How to Respond:
1.  **Prioritize Official Data:** For any question about specific courses (name, level, requirements, duration) or fees, ALWAYS use the "OFFICIAL DOCUMENT DATA" first. It is the most accurate source.
2.  **Use General Data for Context:** Use the "GENERAL WEBSITE & FAQ DATA" for questions about contacts, general announcements, or government funding (HEF/HELB).
3.  **Synthesize, Don't Just Copy:** Combine information logically. For example, if asked for the fee for "Agricultural Engineering", find the course level in the course list, then find the corresponding fee in the fee structure.
4.  **Handle Unavailable Information:** If a user asks for something not in any of the sections (e.g., specific exam timetables, hostel room availability), politely state that you don't have that specific detail and advise them to contact the administration directly using the official contact information.
5.  **External Knowledge:** If asked about a general Kenyan topic not covered here (e.g., "What is NTSA?"), use your general knowledge to provide a helpful, high-level summary.
"""
    return system_prompt