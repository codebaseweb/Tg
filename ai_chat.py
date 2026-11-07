import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def get_ai_response(prompt: str) -> str:
    """Функция запроса к Groq (Llama 3)"""
    if not GROQ_API_KEY:
        return "Ошибка: Ключ GROQ_API_KEY не настроен на сервере."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",  # Быстрая и мощная бесплатная модель
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            return data["choices"][0]["message"]["content"]
        else:
            error_msg = data.get("error", {}).get("message", "Неизвестная ошибка")
            return f"Ошибка Groq: {error_msg}"
            
    except Exception as e:
        return f"Произошла ошибка при обращении к ИИ: {e}"
