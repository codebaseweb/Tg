import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def get_ai_response(messages: list) -> str:
    """Универсальная функция запроса к Groq с защитой от ошибок типов"""
    if not GROQ_API_KEY:
        return "Ошибка: Ключ GROQ_API_KEY не настроен на сервере."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Жесткая страховка: проверяем, чтобы поле 'content' в каждом сообщении было строго строкой (string)
    cleaned_messages = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")
        if isinstance(content, str) and content.strip():
            cleaned_messages.append({"role": role, "content": content})

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": cleaned_messages
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        data = response.json()

        if response.status_code == 200:
            return data["choices"][0]["message"]["content"]
        else:
            error_msg = data.get("error", {}).get("message", "Неизвестная ошибка")
            return f"Ошибка Groq: {error_msg}"

    except Exception as e:
        return f"Ошибка при обращении к ИИ: {e}"
