from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Простые начальные статы игрока
game_state = {
    "hp": 100,
    "gold": 50,
    "location": "Лесная опушка"
}

def get_start_game_message():
    """Создает стартовый текст и набор кнопок (KeyboardMarkup)"""
    text = (
        f"🌲 **Локация:** {game_state['location']}\n"
        f"🩸 **HP:** {game_state['hp']} | 💰 **Золото:** {game_state['gold']}\n\n"
        "Куда направимся, искатель приключений?"
    )
    
    # Собираем InlineKeyboardButton в ряды (InlineKeyboardMarkup)
    keyboard = [
        [InlineKeyboardButton("🕳 Войти в пещеру", callback_data="go_cave")],
        [InlineKeyboardButton("🎒 Проверить инвентарь", callback_data="check_inv")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    return text, reply_markup

def handle_callback(callback_data: str):
    """Меняет состояние игры в зависимости от нажатой кнопки"""
    if callback_data == "go_cave":
        game_state["hp"] -= 10
        text = "🦇 Ты зашел в пещеру, получил по голове от летучей мыши (-10 HP)!"
    elif callback_data == "check_inv":
        text = "🎒 В твоем инвентаре: Ржавый меч, зелье лечения."
    else:
        text = "Неизвестное действие."

    # Обновляем текст со статами
    text += f"\n\n🩸 HP: {game_state['hp']} | 💰 Золото: {game_state['gold']}"

    # Возвращаем кнопку «Назад»
    keyboard = [
        [InlineKeyboardButton("🔙 На развилку", callback_data="go_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    return text, reply_markup
