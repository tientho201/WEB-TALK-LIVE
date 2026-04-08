import os
from groq import Groq

def transcribe_audio(file_path: str) -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(file_path), file.read()),
            model="whisper-large-v3-turbo",
            prompt="这是一段中文语音，请精准转录成简体中文文字。",
            response_format="json",
            language="zh" # Enforce Chinese recognition
        )
    return transcription.text
