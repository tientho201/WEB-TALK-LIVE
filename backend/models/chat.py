from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatResponse(BaseModel):
    user_text: str
    bot_text: str
    audio_path: str


class ChatHistory(ChatResponse):
    id: int
    session_id: Optional[str] = None
    created_at: datetime


class SessionResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
