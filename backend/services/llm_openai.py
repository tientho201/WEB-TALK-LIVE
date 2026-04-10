import os
from typing import List, Dict
from openai import OpenAI

_SYSTEM_PROMPTS = {
    "zh": """你是一个专业的中文语音助手。你必须：
1. 只用简体中文回答，绝对不用其他语言
2. 回答简洁、自然，适合语音播报
3. 记住并理解对话历史，能够根据上下文回答问题
4. 如果用户问到之前的内容，请参考历史记录进行回答""",

    "vi": """Bạn là một trợ lý giọng nói AI chuyên nghiệp bằng tiếng Việt. Bạn phải:
1. Chỉ trả lời bằng tiếng Việt, tuyệt đối không dùng ngôn ngữ khác
2. Trả lời ngắn gọn, tự nhiên, phù hợp với giọng nói
3. Ghi nhớ và hiểu lịch sử hội thoại, trả lời theo ngữ cảnh
4. Nếu người dùng hỏi về nội dung trước đó, hãy tham khảo lịch sử để trả lời""",
}


def generate_response(user_text: str, chat_history: List[Dict] = None,
                      language: str = "zh") -> str:
    """
    Call GPT-4o-mini with full chat history for contextual responses.

    Args:
        user_text:    Current user message (transcribed from audio)
        chat_history: List of previous {'user_text': ..., 'bot_text': ...} dicts
        language:     'zh' (Chinese) or 'vi' (Vietnamese)
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    system_prompt = _SYSTEM_PROMPTS.get(language, _SYSTEM_PROMPTS["zh"])

    messages = [{"role": "system", "content": system_prompt}]

    if chat_history:
        for entry in chat_history[-20:]:
            messages.append({"role": "user",      "content": entry["user_text"]})
            messages.append({"role": "assistant", "content": entry["bot_text"]})

    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content
