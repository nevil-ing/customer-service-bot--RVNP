import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import uvicorn

#Custom services
from .services.data_loader import load_and_process_rag_data
from .services.prompt_builder import create_system_prompt


load_dotenv()



print("Loading RAG data and building system prompt...")
rag_data = load_and_process_rag_data()
SYSTEM_INSTRUCTION = create_system_prompt(rag_data)
print("System prompt created successfully.")


app = FastAPI(
    title="Customer Service Bot",
    description="A FastAPI-based chatbot for the RVNP website.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "views" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "views" / "templates")

class ChatRequest(BaseModel):
    message: str
# groq config
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set. Please add it to your .env file.")
client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1", 
)

#In-memory Chat Sessions
#chat_sessions = {}

#Routes
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", tags=["Chatbot"])
async def chat(chat_request: ChatRequest, request: Request):
    try:
        user_message = chat_request.message
        
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_message}
        ]

      

       # API call
        response = client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        bot_response = response.choices[0].message.content
        return JSONResponse(content={'response': bot_response})

    except Exception as e:
        logging.exception("Chat error:")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
        