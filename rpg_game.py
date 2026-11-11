import os
import random
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 1. СТАТЫ ИГРОКА (добавили слоты для брони и квестовый прогресс)
player = {
    "name": "Странник",
    "hp": 100,
    "max_hp": 100,
    "attack": 15,
    "defense": 0,      # Защита от брони
    "potions": 3,
    "gold": 60,
    "weapon": "Ржавый меч",
    "armor": "Обноски",
    "location": "camp",
    "current_monster": None,
    "quests": {
        "elder_1": {"title": "Очистить Мрачный Лес от гоблинов", "target": 3, "progress": 0, "reward_gold": 50, "completed": False},
        "elder_2": {"title": "Уничтожить монстров в Пещере", "target": 3, "progress": 0, "reward_gold": 100, "completed": False},
        "trader_1": {"title": "Добыть кости из Проклятой Крипты", "target": 2, "progress": 0, "reward_gold": 120, "completed": False}
    }
}

rpg_history = []

# 2. БАЗА ЛОКАЦИЙ И МОНСТРОВ
LOCATIONS = {
    "camp": {
        "name": "Лагерь Выживших",
        "description": "Безопасно у костра. Здесь живут старейшина, торговец и охотник."
    },
    "forest": {
        "name": "Мрачный Лес",
        "monsters": [
            {"name": "Дикий Гоблин", "hp": 30, "damage": 10},
            {"name": "Ядовитый Паук", "hp": 25, "damage": 12},
            {"name": "Лесной Разбойник", "hp": 45, "damage": 15}
        ]
    },
    "cave": {
        "name": "Тёмная Пещера",
        "monsters": [
            {"name": "Пещерный Орк", "hp": 60, "damage": 20},
            {"name": "Огромная Летучая Мышь", "hp": 40, "damage": 18},
            {"name": "Каменный Голем", "hp": 90, "damage": 25}
        ]
    },
    "crypt": {
        "name": "Проклятая Крипта",
        "monsters": [
            {"name": "Скелет-Воин", "hp": 70, "damage": 22},
            {"name": "Зомби", "hp": 85, "damage": 19},
            {"name": "Древний Лиш", "hp": 120, "damage": 33}
        ]
    }
}

def reset_game(user_name: str):
    player["name"] = user_name
    player["hp"] = 100
    player["max_hp"] = 100
    player["attack"] = 15
    player["defense"] = 0
    player["potions"] = 3
    player["gold"] = 60
    player["weapon"] = "Ржавый меч"
    player["armor"] = "Обноски"
    player["location"] = "camp"
    player["current_monster"] = None
    # Сбрасываем квесты
    for q_id in player["quests"]:
        player["quests"][q_id]["progress"] = 0
        player["quests"][q_id]["completed"] = False
    rpg_history.clear()


# 3. ГЕНЕРАТОР КНОПОК ДЛЯ ЛАГЕРЯ И NPC
def generate_dynamic_keyboard():
    keyboard = []

    if player["location"] == "camp":
        # Меню выбора действий в лагере
        keyboard.append([InlineKeyboardButton("📜 Меню Квестов (NPC)", callback_data="npc_menu")])
        keyboard.append([InlineKeyboardButton("🛒 Лавка Торговца (Снаряжение)", callback_data="shop_menu")])
        keyboard.append([InlineKeyboardButton("🌲 Отправиться в Мрачный Лес", callback_data="goto_forest")])
        keyboard.append([InlineKeyboardButton("🕳 Спуститься в Тёмную Пещеру", callback_data="goto_cave")])
        keyboard.append([InlineKeyboardButton("⚰️ Войти в Проклятую Крипту", callback_data="goto_crypt")])

    elif player["location"] == "npc_hub":
        # Список доступных NPC с заданиями
        keyboard.append([InlineKeyboardButton("👴 Староста Марк (Задания лагеря)", callback_data="quest_elder")])
        keyboard.append([InlineKeyboardButton("🧔 Торговец Томас (Заказы на лут)", callback_data="quest_trader")])
        keyboard.append([InlineKeyboardButton("🏘 Вернуться к костру", callback_data="goto_camp")])

    elif player["location"] == "shop_hub":
        # Покупка брони и зелий у торговца
        keyboard.append([InlineKeyboardButton("🛡 Купить Кожаную бронь (Зщт +5) - 80💰", callback_data="buy_armor_1")])
        keyboard.append([InlineKeyboardButton("🛡 Купить Железные латы (Зщт +15) - 200💰", callback_data="buy_armor_2")])
        keyboard.append([InlineKeyboardButton("⚔️ Купить Стальной меч (Урон +15) - 150💰", callback_data="buy_sword_1")])
        keyboard.append([InlineKeyboardButton("🧪 Купить зелье здоровья - 25💰", callback_data="buy_potion")])
        keyboard.append([InlineKeyboardButton("🏘 Вернуться к костру", callback_data="goto_camp")])

    elif player["current_monster"] is not None:
        keyboard.append([InlineKeyboardButton(f"⚔️ Атаковать ({player['weapon']})", callback_data="attack_monster")])
        keyboard.append([InlineKeyboardButton("🏃‍♂️ Сбежать в Лагерь", callback_data="goto_camp")])

    else:
        keyboard.append([InlineKeyboardButton("🔍 Искать нового врага", callback_data=f"search_{player['location']}")])
        keyboard.append([InlineKeyboardButton("🏘 Вернуться в Лагерь", callback_data="goto_camp")])

    if player["hp"] < 50 and player["potions"] > 0:
        keyboard.append([InlineKeyboardButton(f"💊 Выпить зелье (Осталось: {player['potions']})", callback_data="use_potion")])

    return InlineKeyboardMarkup(keyboard)


# 4. ОБЩЕНИЕ С GROQ
async def ask_game_master(action_description: str) -> str:
    if not GROQ_API_KEY:
        return "Ошибка: Ключ Groq не настроен."

    system_prompt = (
        "Ты — мрачный Гейм-Мастер в текстовой RPG в стиле Dark Fantasy. "
        "Описывай диалоги с NPC, квесты и сражения атмосферно, кратко (2-3 предложения). "
        f"Игрока зовут {player['name']}, у него {player['hp']} HP."
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
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            rpg_history.append({"role": "user", "content": action_description})
            rpg_history.append({"role": "assistant", "content": reply})
            return reply
        else:
            return "Тьма скрывает ответы Гейм-Мастера."
    except Exception as e:
        return f"Связь с миром оборвалась: {e}"


# 5. ИГРОВОЙ ДВИЖОК
async def handle_rpg_action(callback_data: str, user_name: str):
    extra_msg = ""

    if callback_data == "start_rpg":
        reset_game(user_name)
        story = await ask_game_master(f"Герой {user_name} прибывает в лагерь. Вокруг суетятся жители, у костра сидит Староста Марк.")

    elif callback_data == "npc_menu":
        player["location"] = "npc_hub"
        story = await ask_game_master("Игрок подходит к палаткам местных жителей. Староста Марк и торговец Томас готовы дать поручения.")

    elif callback_data == "shop_menu":
        player["location"] = "shop_hub"
        story = await ask_game_master("Игрок заходит в тусклую лавку торговца. На полках разложены блестящие клинки и доспехи.")

    elif callback_data == "quest_elder":
        q1 = player["quests"]["elder_1"]
        q2 = player["quests"]["elder_2"]
        status_1 = "✅ Выполнено" if q1["completed"] else f"Прогресс: {q1['progress']}/{q1['target']}"
        status_2 = "✅ Выполнено" if q2["completed"] else f"Прогресс: {q2['progress']}/{q2['target']}"
        extra_msg = f"\n\n📜 **ЗАДАНИЯ СТАРОСТЫ:**\n1. {q1['title']} [{status_1}] (Награда: {q1['reward_gold']}💰)\n2. {q2['title']} [{status_2}] (Награда: {q2['reward_gold']}💰)"
        story = await ask_game_master("Староста Марк с надеждой смотрит на героя и просит очистить окрестности от нечисти.")

    elif callback_data == "quest_trader":
        qt = player["quests"]["trader_1"]
        status_trader = "✅ Выполнено" if qt["completed"] else f"Прогресс: {qt['progress']}/{qt['target']}"
        extra_msg = f"\n\n📜 **ЗАКАЗЫ ТОРГОВЦА:**\n- {qt['title']} [{status_trader}] (Награда: {qt['reward_gold']}💰)"
        story = await ask_game_master("Торговец Томас трет руки и предлагает выгодную сделку по сбору ценных трофеев в крипте.")

    # Покупка предметов у торговца
    elif callback_data == "buy_armor_1":
        if player["gold"] >= 80:
            player["gold"] -= 80
            player["armor"] = "Кожаная броня"
            player["defense"] = 5
            story = "🛡 Игрок покупает и надевает прочную Кожаную броню (+5 защиты)."
        else:
            story = "❌ Недостаточно золота для покупки кожи!"

    elif callback_data == "buy_armor_2":
        if player["gold"] >= 200:
            player["gold"] -= 200
            player["armor"] = "Железные латы"
            player["defense"] = 15
            story = "🛡 Игрок приобретает тяжелые Железные латы (+15 защиты). Теперь он как крепость!"
        else:
            story = "❌ Недостаточно золота для железных лат!"

    elif callback_data == "buy_sword_1":
        if player["gold"] >= 150:
            player["gold"] -= 150
            player["weapon"] = "Стальной меч"
            player["attack"] = 30
            story = "⚔️ Торговец передает острый Стальной меч (+30 атаки)."
        else:
            story = "❌ Не хватает золота на стальной меч!"

    elif callback_data == "buy_potion":
        if player["gold"] >= 25:
            player["gold"] -= 25
            player["potions"] += 1
            story = "🧪 Игрок покупает целебное зелье у торговца."
        else:
            story = "❌ У вас мало золота для покупки зелья!"

    elif callback_data.startswith("goto_"):
        loc_key = callback_data.split("_")[1]
        if loc_key == "camp":
            player["location"] = "camp"
            player["current_monster"] = None
            story = await ask_game_master("Игрок возвращается в Лагерь Выживших к костру.")
        else:
            player["location"] = loc_key
            raw_monster = random.choice(LOCATIONS[loc_key]["monsters"])
            player["current_monster"] = dict(raw_monster)
            story = await ask_game_master(f"Игрок исследует локацию '{LOCATIONS[loc_key]['name']}'. Из засады нападает монстр: {player['current_monster']['name']}!")

    elif callback_data.startswith("search_"):
        loc_key = callback_data.split("_")[1]
        raw_monster = random.choice(LOCATIONS[loc_key]["monsters"])
        player["current_monster"] = dict(raw_monster)
        story = await ask_game_master(f"Игрок продолжает поиски и натыкается на противника: {player['current_monster']['name']}.")

    elif callback_data == "attack_monster":
        monster = player["current_monster"]
        monster["hp"] -= player["attack"]
        
        if monster["hp"] > 0:
            # Урон с учетом брони игрока
            actual_damage = max(5, monster["damage"] - player["defense"])
            player["hp"] -= actual_damage
            story = await ask_game_master(f"Игрок бьет монстра {monster['name']}. В ответ получает удар, но броня ({player['armor']}) смягчает урон (-{actual_damage} HP)!")
        else:
            # Победа над монстром и выдача лута
            gold_drop = random.randint(20, 60)
            player["gold"] += gold_drop
            loot_parts = [f"💰 Золото: +{gold_drop}"]

            # Прогресс квестов в зависимости от локации
            if player["location"] == "forest":
                q = player["quests"]["elder_1"]
                if not q["completed"]:
                    q["progress"] += 1
                    if q["progress"] >= q["target"]:
                        q["completed"] = True
                        player["gold"] += q["reward_gold"]
                        loot_parts.append(f"🎉 КВЕСТ ВЫПОЛНЕН: '{q['title']}' (+{q['reward_gold']}💰)!")

            elif player["location"] == "cave":
                q = player["quests"]["elder_2"]
                if not q["completed"]:
                    q["progress"] += 1
                    if q["progress"] >= q["target"]:
                        q["completed"] = True
                        player["gold"] += q["reward_gold"]
                        loot_parts.append(f"🎉 КВЕСТ ВЫПОЛНЕН: '{q['title']}' (+{q['reward_gold']}💰)!")

            elif player["location"] == "crypt":
                qt = player["quests"]["trader_1"]
                if not qt["completed"]:
                    qt["progress"] += 1
                    if qt["progress"] >= qt["target"]:
                        qt["completed"] = True
                        player["gold"] += qt["reward_gold"]
                        loot_parts.append(f"🎉 КВЕСТ ТОРГОВЦА ВЫПОЛНЕН! (+{qt['reward_gold']}💰)!")

            if random.random() < 0.4:
                player["potions"] += 1
                loot_parts.append("🧪 Найдено зелье!")

            extra_msg = "\n\n🎁 **ЛУТ И НАГРАДЫ:** " + " | ".join(loot_parts)
            story = await ask_game_master(f"Игрок уничтожает монстра {monster['name']}! Враг повержен.")
            player["current_monster"] = None

    elif callback_data == "use_potion":
        if player["potions"] > 0:
            player["potions"] -= 1
            player["hp"] = min(player["max_hp"], player["hp"] + 50)
            story = f"🧪 {player['name']} выпивает целебное зелье. Здоровье восстановлено!"
        else:
            story = "❌ У вас нет зелий лечения!"

    else:
        story = "Неизвестное действие."

    # Обработка смерти
    if player["hp"] <= 0:
        player["hp"] = 100
        player["current_monster"] = None
        player["location"] = "camp"
        death_notice = "💀 **ВЫ ПОГИБЛИ В БОЮ!** Темные силы возвращают вас к спасительному костру в лагере...\n\n"
        status_header = (
            f"⚔️ **Герой:** {player['name']} | 🗡 {player['weapon']} | 🛡 {player['armor']}\n"
            f"🩸 **HP:** {player['hp']}/{player['max_hp']} | 🛡 Защита: {player['defense']} | 💰 {player['gold']}\n"
            f"----------------------------------------\n\n"
        )
        return status_header + death_notice + "Вы приходите в себя в лагере.", generate_dynamic_keyboard()

    # Шапка интерфейса
    loc_name = "Лагерь Выживших"
    if player["location"] == "npc_hub":
        loc_name = "Палатки NPC (Квесты)"
    elif player["location"] == "shop_hub":
        loc_name = "Лавка Торговца"
    elif player["location"] in LOCATIONS:
        loc_name = LOCATIONS[player["location"]]["name"]

    monster_info = ""
    if player["current_monster"]:
        m = player["current_monster"]
        monster_info = f"\n⚠️ **Враг:** {m['name']} | 🩸 HP монстра: {m['hp']}"

    status_header = (
        f"⚔️ **Герой:** {player['name']} | 🗡 {player['weapon']} | 🛡 {player['armor']}\n"
        f"🩸 **HP:** {player['hp']}/{player['max_hp']} | 🛡 Защита: {player['defense']} | 🧪 Зелья: {player['potions']} | 💰 {player['gold']}\n"
        f"📍 **Локация:** {loc_name}"
        f"{monster_info}\n"
        f"----------------------------------------\n\n"
    )

    return status_header + story + extra_msg, generate_dynamic_keyboard()
