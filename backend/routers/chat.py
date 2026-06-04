from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from services.chatbot import get_travel_response_with_meta
from database import list_chat_logs, get_chat_log_stats

router = APIRouter()


class Message(BaseModel):
    role: str       # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: Optional[str] = ""


class ChatResponse(BaseModel):
    reply: str
    meta: Optional[dict] = None


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in request.messages]
    reply, meta = await get_travel_response_with_meta(
        history, session_id=request.session_id or ""
    )
    return ChatResponse(reply=reply, meta=meta)


@router.get("/logs")
def get_logs(
    limit: int = Query(default=100, ge=1, le=1000),
    session_id: str = Query(default=""),
):
    """Return recent chat log rows ordered newest-first."""
    rows = list_chat_logs(limit=limit, session_id=session_id)
    return {"total": len(rows), "logs": rows}


@router.get("/logs/stats")
def get_log_stats():
    """Aggregate token & cost stats grouped by provider/model."""
    return get_chat_log_stats()
