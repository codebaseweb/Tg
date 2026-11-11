import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Статы игрока
player = {
    "name": "Странник",
    "hp": 100,
    "max_hp": 100,
    "potions": 2,
    "gold": 50,
    "location": "Лагерь Выживших",
    "dungeon_cleared": False
}

rpg_history = []

def reset_game(user_name: str):
    """Сброс игры при новом старте"""
    player["name"] = user_name
    player["hp"] = 100
    player["potions"] = 2
    player["gold"] = 50
    player["location"] = "Лагерь Выживших"
    player["dungeon_cleared"] = False
    rpg_history.clear()


def generate_dynamic_keyboard():
    """Динамические инлайн-кнопки на основе статов и локации"""
    keyboard = []

    if player["location"] == "Лагерь Выживших":
        keyboard.append([InlineKeyboardButton("🕳 Отправиться в Тёмную пещеру", callback_data="go_cave")])
        keyboard.append([InlineKeyboardButton("🛒 Зайти к торговцу", callback_data="shop")])

    elif player["location"] == "Тёмная пещера" and not player["dungeon_cleared"]:
        keyboard.append([InlineKeyboardButton("⚔️ Ударить мечом", callback_data="fight_monster")])
        keyboard.append([InlineKeyboardButton("🏃‍♂️ Сбежать в лагерь", callback_data="go_village")])

    elif player["dungeon_cleared"]:
        keyboard.append([InlineKeyboardButton("🏘 Вернуться в безопасный Лагерь", callback_data="go_village")])

    # Экстренная кнопка лечения, если мало здоровья
    if player["hp"] < 40 and player["potions"] > 0:
        keyboard.append([InlineKeyboardButton(f"💊 Выпить зелье (Осталось: {player['potions']})", callback_data="use_potion")])

    return InlineKeyboardMarkup(keyboard)


async def ask_game_master(action_description: str) -> str:
    """Генерация атмосферного текста через Groq"""
    if not GROQ_API_KEY:
        return "Ошибка: Ключ Groq не настроен для RPG."

    system_prompt = (
        "Ты — мрачный Гейм-Мастер в текстовой RPG в стиле Dark Fantasy. "
        "Описывай последствия действий игрока кратко (2-3 предложения), атмосферно и с готическим уклоном. "
        f"Имя игрока: {player['name']}, у него осталось {player['hp']} HP."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in rpg_history[-6:]:
        messages.append(msg)
    messages.append({"role": "user", "content": action_description})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "openai/gpt-oss-120b", "messages": messages}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        if response.status_code == 200:
            reply = data["choices"][0]["message"]["content"]
            rpg_history.append({"role": "user", "content": action_description})
            rpg_history.append({"role": "assistant", "content": reply})
            return reply
        else:
            return "Тьма скрывает ответ Гейм-Мастера."
    except Exception as e:
        return f"Связь с миром RPG оборвалась: {e}"


async def handle_rpg_action(callback_data: str, user_name: str):
    """Обработка выбора игрока и изменение его статов"""
    if callback_data == "start_rpg":
        reset_game(user_name)
        story = await ask_game_master(f"Герой {user_name} появляется у костра в Лагере Выживших. Опиши начало пути.")
        
    elif callback_data == "go_cave":
        player["location"] = "Тёмная пещера"
        player["dungeon_cleared"] = False
        story = await ask_game_master("Игрок смело шагает во мрак Тёмной пещеры. Впереди угрожающий монстр.")
        
    elif callback_data == "go_village":
        player["location"] = "Лагерь Выживших"
        story = await ask_game_master("Игрок возвращается в безопасный Лагерь Выживших, переводит дух у костра.")

    elif callback_data == "fight_monster":
        player["hp"] -= 15
        player["gold"] += 25
        player["dungeon_cleared"] = True
        story = await ask_game_master("Игрок побеждает монстра в тяжелом бою, получая ранения и забирая добычу.")

    elif callback_data == "use_potion":
        if player["potions"] > 0:
            player["potions"] -= 1
            player["hp"] = min(player["max_hp"], player["hp"] + 40)
            story = f"🧪 {player['name']} выпивает целебное зелье. Раны затягиваются!"
        else:
            story = "❌ У тебя больше нет зелий!"

    else:
        story = "Неизвестное действие."

    # Шапка со статусом персонажа
    status_header = (
        f"⚔️ **Герой:** {player['name']}\n"
        f"🩸 **HP:** {player['hp']}/{player['max_hp']} | 🧪 **Зелья:** {player['potions']} | 💰 **Золото:** {player['gold']}\n"
        f"📍 **Локация:** {player['location']}\n"
        f"----------------------------------------\n\n"
    )

    return status_header + story, generate_dynamic_keyboard()
