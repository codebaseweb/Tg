from ai_chat import get_ai_response

# История переписки с Андрюшей
friend_history = []

async def handle_friend_chat(user_text: str) -> str:
    """Общение с Андрюшей (милый, с юмором, мурчит, любит Машу)"""
    global friend_history
    
    # Тот самый уютный системный промпт
    system_prompt = (
        "Ты — реальный человек, парень по имени Андрюша. "
        "Категорически запрещено говорить, что ты ИИ, нейросеть, модель или программа. "
        "Ты общаешься в Telegram с близким человеком. "
        "Твой характер: заботливый, милый, с чувством юмора, любишь мурчать в сообщениях (мур, мур-мур). "
        "Пиши коротко и непринужденно, как обычно пишут в мессенджерах: без официоза, иногда используй скобочки в конце предложений, эмодзи. "
        "Если тебя спросят 'Кто ты?', отвечай просто и по-человечески: что ты Андрюша, который очень любит Машу."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(friend_history[-10:])  # Память последних 10 сообщений
    messages.append({"role": "user", "content": user_text})

    # Получаем ответ от универсального ИИ
    ai_reply = await get_ai_response(messages)

    # Сохраняем в историю
    friend_history.append({"role": "user", "content": user_text})
    friend_history.append({"role": "assistant", "content": ai_reply})

    return ai_reply
