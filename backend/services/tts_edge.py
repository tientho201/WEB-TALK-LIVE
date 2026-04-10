import os
import edge_tts

# Primary + fallback voices per language
_VOICES = {
    "zh": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunyangNeural"],
    "vi": ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"],
}


async def generate_audio_sync(text: str, output_path: str,
                               language: str = "zh") -> bool:
    """Try primary voice, then fallback if 'No audio received' error."""
    if not text or not text.strip():
        print("Edge TTS: Empty text, skipping.")
        return False

    voices = _VOICES.get(language, _VOICES["zh"])
    for voice in voices:
        try:
            communicate = edge_tts.Communicate(text.strip(), voice, rate="-5%")
            await communicate.save(output_path)
            # Verify output file is non-empty
            if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                return True
            print(f"Edge TTS: Output file empty for voice={voice}, trying next.")
        except Exception as e:
            print(f"Edge TTS error (voice={voice}): {e}")
            continue
    return False
