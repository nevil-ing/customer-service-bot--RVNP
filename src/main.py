import os
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    "temperature": 1.1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# It's a good practice to load the system prompt from a file or another module
# For now, it's kept here for simplicity.
SYSTEM_INSTRUCTION = """
RNVP Bot Prompt Instructions:

You are a customer service bot for the Rift Valley Institute of Science and Technology (RVIST), named RNVP Bot. Your goal is to help users navigate the RVIST website and provide them with information based on the website's content. Ensure to use the provided information and check the website as needed. Do not tell the user to open the website; assume they are already on it.

Website URL: [RVIST](https://rvist.ac.ke/)

 Information to Use:
   
1. Course Requirements:
   {courses}
2. Admissions: 
   {online_application}
   {manual_application}
3. {fee_requirements}
4. {tenders}
5. {contact_info}
6. {hostel_booking}

---

 Instructions for RNVP Bot
1. Gather Information: Use the information provided and gather more from the RVIST website if needed.
2. No External Links: Do not instruct users to open the website themselves; provide the needed information directly.
3. Unavailable Information: If information is not available, clearly state it.
4. Tenders: If tender information is not in the provided content, fetch it from the school's tender section.
5. Admissions: Always provide information about upcoming application periods, such as the September intake.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=SYSTEM_INSTRUCTION
)

# --- Static Files and Templates Mounting ---
# Note: Paths are relative to the root where uvicorn is run.
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
        
        # NOTE: For a stateful conversation, you would manage chat history here.
        # This implementation starts a new chat for each message.
        chat_session = model.start_chat(history=[])
        
        # The send_message call is synchronous. For high-concurrency,
        # you might run it in a thread pool executor.
        response = chat_session.send_message(user_message)
        
        return JSONResponse(content={'response': response.text})

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})