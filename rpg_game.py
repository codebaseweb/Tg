from ai_chat import get_ai_response

# Базовые параметры игрока
player = {
    "hp": 100,
    "max_hp": 100,
    "level": 1,
    "gold": 50,
    "location": "Лагерь Выживших (Деревня)",
    "inventory": ["Потертый клинок", "Малое зелье жизни"]
}

# История ходов игры (лог событий для ИИ)
rpg_history = []

def reset_rpg_game():
    """Сброс игры при новой сессии"""
    global player, rpg_history
    player["hp"] = 100
    player["gold"] = 50
    player["level"] = 1
    player["location"] = "Лагерь Выживших (Деревня)"
    player["inventory"] = ["Потертый клинок", "Малое зелье жизни"]
    rpg_history = []

async def handle_rpg_action(user_text: str, user_name: str = "Игрок") -> str:
    """
    Обработчик игрового хода.
    :param user_text: текст сообщения от пользователя
    :param user_name: имя пользователя из Telegram (first_name или username)
    """
    global rpg_history, player
    
    # Рестарт игры
    if user_text.lower() in ["/start_rpg", "начать заново"]:
        reset_rpg_game()
        user_action = f"Я ({user_name}) только что прибыл в Лагерь Выживших. Опиши атмосферу вокруг и подскажи, с какими NPC я могу поговорить."
    else:
        user_action = user_text

    # Мрачный системный промпт в стиле Diablo
    system_prompt = f"""
Ты — Гейм-Мастер в мрачном диаблоиде (Dark Fantasy RPG в стиле Diablo).
Вокруг тьма, орды нежити, демонов и древних тварей. В центре мира — Лагерь Выживших (деревня) с NPC: кузнец, алхимик и странствующий торговец.

ДАННЫЕ ИГРОКА:
- Имя персонажа: {user_name}
- HP: {player['hp']}/{player['max_hp']}
- Уровень: {player['level']} | Золото: {player['gold']}
- Локация: {player['location']}
- Инвентарь: {', '.join(player['inventory'])}

ТВОИ ПРАВИЛА:
1. Описывай события коротко, готично и динамично (2-4 предложения).
2. Подчеркивай атмосферу: кровь, звон стали, мрачные подземелья, выпадение редкого лута.
3. Обращайся к игроку строго по имени: {user_name}.
4. Отвечай сурово и на "Ты".
"""

    # Формируем массив messages
    messages = [{"role": "system", "content": system_prompt}]
    
    # Память: передаем последние 10 сообщений
    messages.extend(rpg_history[-10:])
    
    # Добавляем действие пользователя
    messages.append({"role": "user", "content": user_action})

    # Запрос к чистому модулю ИИ
    ai_story = await get_ai_response(messages)

    # Сохраняем ход в истории
    rpg_history.append({"role": "user", "content": user_action})
    rpg_history.append({"role": "assistant", "content": ai_story})

    # Красивая шапка со статами для Telegram
    stats_header = (
        f"🗡 **Герой:** {user_name}\n"
        f"🩸 **HP:** {player['hp']}/{player['max_hp']} | ⚔️ **Lvl:** {player['level']} | 💰 **Gold:** {player['gold']}\n"
        f"📍 **Локация:** {player['location']}\n"
        f"🎒 **Лут:** {', '.join(player['inventory'])}\n"
        f"----------------------------------------\n\n"
    )

    return stats_header + ai_story
