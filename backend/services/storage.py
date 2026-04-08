import os
import requests as req_lib

# ─── Config ──────────────────────────────────────────────────────────────────── #
# Set STORAGE_BACKEND=supabase in .env for production
STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "local")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "audio-files")
LOCAL_AUDIO_DIR = "audio_files"

os.makedirs(LOCAL_AUDIO_DIR, exist_ok=True)


def save_audio_file(local_path: str, filename: str) -> str:
    """
    Saves the audio file and returns the stored path/URL.

    LOCAL  → returns 'audio_files/{filename}' (served by FastAPI static mount)
    SUPABASE → uploads to Supabase Storage bucket and returns the public URL
    """
    if STORAGE_BACKEND == "supabase" and SUPABASE_URL and SUPABASE_SERVICE_KEY:
        return _upload_to_supabase(local_path, filename)
    # Default: file is already saved locally, just return relative path
    return f"{LOCAL_AUDIO_DIR}/{filename}"


def _upload_to_supabase(local_path: str, filename: str) -> str:
    """Upload audio to Supabase Storage and return public URL."""
    with open(local_path, "rb") as f:
        audio_data = f.read()

    upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "audio/mpeg",
        "x-upsert": "true",  # Overwrite if exists
    }
    res = req_lib.post(upload_url, data=audio_data, headers=headers, timeout=30)
    if res.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        return public_url
    raise Exception(f"Supabase Storage upload failed ({res.status_code}): {res.text}")


def resolve_audio_url(stored_path: str, backend_url: str = "") -> str:
    """
    Converts stored path to a playable URL.
    - If already a full URL (Supabase), return as-is.
    - If local path, prepend backend URL.
    """
    if stored_path.startswith("http"):
        return stored_path
    return f"{backend_url}/{stored_path}"
