import os
from typing import List, Dict
from openai import OpenAI

SYSTEM_PROMPT = """你是一个专业的中文语音助手。你必须：
1. 只用简体中文回答，绝对不用其他语言
2. 回答简洁、自然，适合语音播报
3. 记住并理解对话历史，能够根据上下文回答问题
4. 如果用户问到之前的内容，请参考历史记录进行回答"""


def generate_response(user_text: str, chat_history: List[Dict] = None) -> str:
    """
    Call GPT-4o-mini with full chat history for contextual responses.

    Args:
        user_text: The current user message (already transcribed from audio)
        chat_history: List of previous {'user_text': ..., 'bot_text': ...} dicts
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Inject conversation history (last 20 exchanges max to avoid token overflow)
    if chat_history:
        for entry in chat_history[-20:]:
            messages.append({"role": "user", "content": entry["user_text"]})
            messages.append({"role": "assistant", "content": entry["bot_text"]})

    # Add current user message
    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content
