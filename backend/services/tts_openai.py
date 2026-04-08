import os
from openai import AsyncOpenAI

async def generate_audio_fallback(text: str, output_path: str) -> bool:
    try:
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = await client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        response.stream_to_file(output_path)
        return True
    except Exception as e:
        print(f"OpenAI TTS fallback encountered an error: {e}")
        return False
