# Словарь для хранения простого прогресса игроков (в памяти)
players = {}

def start_game(user_id):
    """Инициализация или запуск игры для игрока"""
    if user_id not in players:
        players[user_id] = {"hp": 100, "location": "Стартовая деревня"}
    
    p = players[user_id]
    return f"📜 Добро пожаловать в RPG!\n📍 Локация: {p['location']}\n❤️ Здоровье: {p['hp']}\n\nКуда хочешь отправиться?"
