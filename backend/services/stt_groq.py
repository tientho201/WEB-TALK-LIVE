import os
from groq import Groq

# Language configs for Groq Whisper
_LANG_CONFIGS = {
    "zh": {
        "language": "zh",
        "prompt": "这是一段中文语音，请精准转录成简体中文文字。",
    },
    "vi": {
        "language": "vi",
        "prompt": "Đây là giọng nói tiếng Việt, hãy chuyển đổi thành văn bản tiếng Việt chính xác.",
    },
}

# Known Whisper hallucination phrases (case-insensitive substring match)
# Whisper hallucinates these when it receives silence, noise, or unclear audio.
_HALLUCINATION_TOKENS = [
    "subscribe",
    "ghiền mì gõ",
    "like and subscribe",
    "thank you for watching",
    "please subscribe",
    "đăng ký kênh",
    "bấm vào đây",
    "xem thêm video",
    "chia sẻ video",
    "cảm ơn đã xem",
    "thanks for watching",
    "don't forget to",
    "hit the bell",
    "comment below",
    "ご视聴ありがとう",
    "谢谢观看",
    "记得订阅",
    "点赞关注",
]

# Minimum number of characters for a valid transcription
_MIN_TEXT_LENGTH = 3


class STTHallucinationError(Exception):
    """Raised when Whisper returns a hallucinated (non-speech) result."""
    pass


def _is_hallucination(text: str) -> bool:
    """Detect Whisper hallucination by checking against known bogus phrases."""
    lower = text.lower().strip()
    if len(lower) < _MIN_TEXT_LENGTH:
        return True
    for token in _HALLUCINATION_TOKENS:
        if token in lower:
            return True
    return False


def transcribe_audio(file_path: str, language: str = "zh") -> str:
    """
    Transcribe audio via Groq Whisper.

    Raises:
        STTHallucinationError: If the result looks like Whisper hallucination
                               (silence, noise, or unrecognizable speech).
    """
    cfg = _LANG_CONFIGS.get(language, _LANG_CONFIGS["zh"])
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(file_path), file.read()),
            model="whisper-large-v3-turbo",
            prompt=cfg["prompt"],
            response_format="json",
            language=cfg["language"],
        )

    text = transcription.text.strip()
    print(f"[STT] Transcribed ({language}): {repr(text)}")

    if _is_hallucination(text):
        lang_name = "tiếng Việt" if language == "vi" else "中文"
        raise STTHallucinationError(
            f"Không nhận diện được giọng nói. "
            f"Vui lòng nói rõ hơn bằng {lang_name} và thử lại."
            if language == "vi" else
            f"无法识别语音，请用{lang_name}清晰地说话后重试。"
        )

    return text
