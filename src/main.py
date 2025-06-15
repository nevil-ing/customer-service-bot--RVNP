import os
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# Import the new services
from .services.data_loader import load_and_process_rag_data
from .services.prompt_builder import create_system_prompt

# Load environment variables from .env file
load_dotenv()

# --- RAG Data and Prompt Setup (Runs once at application startup) ---
print("Loading RAG data and building system prompt...")
rag_data = load_and_process_rag_data()
SYSTEM_INSTRUCTION = create_system_prompt(rag_data)
print("System prompt created successfully.")
# Optional: print(SYSTEM_INSTRUCTION) to debug the generated prompt

# --- Application Setup ---
app = FastAPI(
    title="Customer Service Bot",
    description="A FastAPI-based chatbot for the RVNP website.",
    version="1.0.0"
)

# --- Pydantic Models for Request/Response ---
class ChatRequest(BaseModel):
    message: str

# --- Gemini API Configuration ---
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=gemini_api_key)

generation_config = {
    "temperature": 0.7, # Lowered for more factual, less creative responses
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=SYSTEM_INSTRUCTION # Use the dynamically generated prompt
)

# --- Static Files and Templates Mounting ---
app.mount("/static", StaticFiles(directory="src/views/static"), name="static")
templates = Jinja2Templates(directory="src/views/templates")

# --- API Endpoints ---
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def serve_frontend(request: Request):
    """
    Serves the main chatbot HTML interface.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", tags=["Chatbot"])
async def chat(chat_request: ChatRequest):
    """
    Handles the chat logic, receiving a message and returning the bot's response.
    """
    try:
        user_message = chat_request.message
        
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_message)
        
        return JSONResponse(content={'response': response.text})

    except Exception as e:
        print(f"Error during chat processing: {e}")
        return JSONResponse(status_code=500, content={'error': 'An internal error occurred.'})