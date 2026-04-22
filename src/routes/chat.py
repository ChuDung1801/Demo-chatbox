# src/routes/chat.py
"""
POST /api/chat           — Send message, get AI response
DELETE /api/chat/session/{session_id} — Clear conversation history
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.langchain_chain.chain import chat, clear_session
from src.data.database import UserRepository

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str  = Field(..., min_length=1, description="Unique session identifier")
    message:    str  = Field(..., min_length=1, max_length=2000)
    user_id:    int | None = Field(default=None, ge=1)

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        return v.strip()


class ChatResponse(BaseModel):
    success:    bool
    session_id: str
    reply:      str
    movie_ids:  list[int]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/", response_model=ChatResponse)
async def send_message(body: ChatRequest) -> ChatResponse:
    """Send a chat message and receive an AI-generated movie recommendation."""

    # Validate user if provided
    if body.user_id and not UserRepository.find_by_id(body.user_id):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy người dùng ID={body.user_id}")

    result = await chat(
        session_id=body.session_id,
        message=body.message,
        user_id=body.user_id,
    )

    return ChatResponse(
        success=True,
        session_id=body.session_id,
        reply=result["text"],
        movie_ids=result["movie_ids"],
    )


@router.delete("/session/{session_id}")
async def reset_session(session_id: str) -> dict:
    """Clear the conversation memory for a session (e.g. when user switches account)."""
    clear_session(session_id)
    return {"success": True, "message": f'Session "{session_id}" đã được xoá.'}
