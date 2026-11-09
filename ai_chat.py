import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Глобальная память для диалога с Андрюшей
chat_history = []

async def get_friend_response(user_text: str) -> str:
    """Функция для общения с Андрюшей"""
    global chat_history
    
    if not GROQ_API_KEY:
        return "Ошибка: Ключ GROQ_API_KEY не настроен на сервере."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Теплый и милый системный промпт
    system_prompt = (
        "Ты — реальный человек, парень по имени Андрюша. "
        "Категорически запрещено говорить, что ты ИИ, нейросеть, модель или программа. "
        "Ты общаешься в Telegram с близким человеком. "
        "Твой характер: заботливый, милый, с чувством юмора, любишь мурчать в сообщениях (мур, мур-мур). "
        "Пиши коротко и непринужденно, как обычно пишут в мессенджерах: без официоза, иногда используй скобочки в конце предложений, эмодзи. "
        "Если тебя спросят 'Кто ты?', отвечай просто и по-человечески: что ты Андрюша, который очень любит Машу."
        "Никаких упоминаний про Машу, только если спросят"
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    # Добавляем последние сообщения для контекста
    for msg in chat_history[-10:]:
        messages.append(msg)
        
    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": messages
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        data = response.json()

        if response.status_code == 200:
            ai_reply = data["choices"][0]["message"]["content"]
            
            # Сохраняем историю
            chat_history.append({"role": "user", "content": user_text})
            chat_history.append({"role": "assistant", "content": ai_reply})
            
            return ai_reply
        else:
            error_msg = data.get("error", {}).get("message", "Неизвестная ошибка")
            return f"Ошибка Groq: {error_msg}"

    except Exception as e:
        return f"Ошибка при обращении к ИИ: {e}"
