import os
import uuid
import shutil
from typing import Optional, List, Dict
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, WebSocket, WebSocketDisconnect, Form
from sqlalchemy.orm import Session
from backend.database.db import get_db, Chat, ChatSession
from backend.routes.auth import get_current_user
from backend.services.stt_groq import transcribe_audio
from backend.services.llm_openai import generate_response
from backend.services.tts_edge import generate_audio_sync
from backend.services.tts_openai import generate_audio_fallback
from backend.services.storage import save_audio_file
from backend.models.chat import ChatResponse

router = APIRouter()
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)


# ─── Session Endpoints (protected) ───────────────────────────────────────── #

@router.post("/sessions")
def create_session(
    name: str = "新对话",
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session_id = str(uuid.uuid4())
    new_session = ChatSession(id=session_id, name=name, user_id=current_user["user_id"])
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"id": new_session.id, "name": new_session.name, "created_at": new_session.created_at}


@router.get("/sessions")
def get_sessions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user["user_id"])
        .order_by(ChatSession.created_at.desc())
        .all()
    )
    return [{"id": s.id, "name": s.name, "created_at": s.created_at} for s in sessions]


# ─── Chat Endpoint (protected) ────────────────────────────────────────────── #

@router.post("/chat", response_model=ChatResponse)
async def process_chat(
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # 1. Save input audio
        input_ext = audio.filename.split(".")[-1] if "." in audio.filename else "wav"
        input_filename = f"{uuid.uuid4()}_input.{input_ext}"
        input_path = os.path.join(AUDIO_DIR, input_filename)
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # 2. Speech → Text
        user_text = transcribe_audio(input_path)

        # 3. Fetch session chat history for GPT context
        chat_history: List[Dict] = []
        if session_id:
            history_records = (
                db.query(Chat)
                .filter(Chat.session_id == session_id)
                .order_by(Chat.created_at.asc())
                .all()
            )
            chat_history = [{"user_text": c.user_text, "bot_text": c.bot_text} for c in history_records]

        # 4. Text → GPT (with history) → Chinese response
        bot_text = generate_response(user_text, chat_history=chat_history)

        # 5. Text → Audio
        output_filename = f"{uuid.uuid4()}_output.mp3"
        output_path = os.path.join(AUDIO_DIR, output_filename)
        success = await generate_audio_sync(bot_text, output_path)
        if not success:
            success = await generate_audio_fallback(bot_text, output_path)
            if not success:
                raise HTTPException(status_code=500, detail="Both TTS engines failed.")

        # 6. Store audio (local or Supabase)
        stored_audio_path = save_audio_file(output_path, output_filename)

        # 7. Save to DB
        chat_record = Chat(
            session_id=session_id,
            user_text=user_text,
            bot_text=bot_text,
            audio_path=stored_audio_path,
        )
        db.add(chat_record)
        db.commit()
        db.refresh(chat_record)

        return ChatResponse(user_text=user_text, bot_text=bot_text, audio_path=stored_audio_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chats")
def get_chats(
    session_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Chat)
    if session_id:
        q = q.filter(Chat.session_id == session_id)
    return q.order_by(Chat.created_at.asc()).all()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            await websocket.send_text("Audio stream bytes received")
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
