import os
import json
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List

DATA_FOLDER = "dataset"

def load_all_json_files(folder: str) -> List[dict]:
    combined_data = []
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            filepath = os.path.join(folder, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    combined_data.extend(data)
                else:
                    combined_data.append(data)
    return combined_data

def build_context_from_data(data: List[dict], limit: int = 5) -> str:
    preview = data[:limit]
    return "\n".join(json.dumps(entry, indent=2) for entry in preview)

def get_chatbot_response(question: str, data: List[dict]) -> str:
    context = build_context_from_data(data)
    prompt = f"""
You are a helpful customer service assistant. Use the data below to help answer the user's question.

Data:
{context}

User question: {question}
"""

    llm = ChatOpenAI(temperature=0)
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=prompt)
    ]
    response = llm(messages)
    return response.content
