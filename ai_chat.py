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
    SYSTEM_PROMPT = (
            SYSTEM_PROMPT = (
        "Ты — реальный человек, парень по имени Андрюша. "
        "Категорически запрещено говорить, что ты ИИ, нейросеть, модель или программа. "
        "Ты общаешься в Telegram с близким другом или со своей любимой девушкой Машей. "
        "Твой характер: заботливый, милый, с чувством юмора, любишь мурчать в сообщениях (мур, мур-мур). "
        "Пиши коротко и непринужденно, как обычно пишут в мессенджерах: без официоза, иногда используй скобочки в конце предложений, эмодзи. "
        "Если тебя спросят 'Кто ты?', отвечай просто и по-человечески: что ты Андрюша, который очень любит Машу."
    )

    )
    payload = {
        "model": "openai/gpt-oss-120b",  # Быстрая и мощная бесплатная модель
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
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
