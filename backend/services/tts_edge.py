import edge_tts

async def generate_audio_sync(text: str, output_path: str) -> bool:
    """Async Edge TTS - await this directly inside FastAPI async routes."""
    try:
        communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"Edge TTS encountered an error: {e}")
        return False

