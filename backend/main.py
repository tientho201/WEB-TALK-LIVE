from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.routes.chat import router as chat_router
from backend.routes.auth import router as auth_router
from backend.database.db import init_db
import os
import glob

AUDIO_DIR = "audio_files"

app = FastAPI(title="Chinese Voice Chat API")

os.makedirs(AUDIO_DIR, exist_ok=True)
app.mount("/audio_files", StaticFiles(directory=AUDIO_DIR), name="audio_files")

app.include_router(auth_router)
app.include_router(chat_router)


def cleanup_audio_files():
    """Delete all audio files on startup to free disk space.
    Chat history (text) in DB is preserved; only local audio blobs are removed.
    """
    patterns = ["*.mp3", "*.wav", "*.m4a", "*.ogg", "*.flac"]
    deleted = 0
    for pattern in patterns:
        for f in glob.glob(os.path.join(AUDIO_DIR, pattern)):
            try:
                os.remove(f)
                deleted += 1
            except Exception as e:
                print(f"[cleanup] Could not delete {f}: {e}")
    print(f"[startup] Cleaned up {deleted} audio file(s) from '{AUDIO_DIR}/'")


@app.on_event("startup")
def startup_event():
    cleanup_audio_files()
    init_db()


@app.get("/")
def health_check():
    return {"status": "running"}
