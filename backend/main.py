import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import chat
from services.chatbot import detect_provider

load_dotenv()

app = FastAPI(
    title="Day5-6-Lap--Hackthon-Travel Chatbot API",
    version="1.0.0",
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/health")
def health():
    provider = detect_provider()
    models = {
        "openai": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        "gemini": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        "claude": os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307"),
        "openrouter": os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
        "ollama": os.getenv("OLLAMA_MODEL", "llama3"),
    }
    return {
        "status": "ok",
        "service": "Travel Chatbot API",
        "ai_provider": provider,
        "model": models.get(provider, "unknown"),
    }
