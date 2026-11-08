import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Подключаем твои модули
import ai_chat
import rpg_game
import ai_friend

# Безопасно получаем токен из настроек Railway
TOKEN = os.getenv("TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Распределение сообщений от пользователя"""
    text = update.message.text
    user_name = update.message.from_user.first_name or "Путешественник"

    # 1. Если нажата кнопка ИИ Чат
    if text == "🤖 ИИ Чат":
        await update.message.reply_text("Андрюша на связи! 🐾 Напиши мне что-нибудь.")
        
    # 2. Если нажата кнопка RPG Игра
    elif text == "🎮 RPG Игра":
        response = await rpg_game.handle_rpg_action("/start_rpg", user_name=user_name)
        await update.message.reply_text(response, parse_mode="Markdown")
        
    # 3. Всё остальное (обычный текст, который ты пишешь в чате)
    else:
        # Здесь сообщения летят к нашему милому Андрюше
        response = await ai_friend.handle_friend_chat(text)
        await update.message.reply_text(response)

        
    else:
        # Здесь определяем, куда отправлять обычный текст пользователя
        # Например, если ты хочешь, чтобы весь свободный текст вне кнопок шел в RPG:
        response = await rpg_game.handle_rpg_action(text, user_name=user_name)
        await update.message.reply_text(response, parse_mode="Markdown")

def main():
    if not TOKEN:
        print("Ошибка: Токен Telegram не найден в переменных окружения!")
        return

    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот успешно запущен и ожидает сообщения...")
    application.run_polling()

if __name__ == "__main__":
    main()
  
