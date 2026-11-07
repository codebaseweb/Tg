import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Используем стабильную модель gemini-pro
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

async def get_ai_response(prompt: str) -> str:
    """Функция запроса к  искусственному интеллекту"""
    if not model:
        return "Ошибка: Ключ GEMINI_API_KEY не настроен на сервере."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Произошла ошибка при обращении к ИИ: {e}"
