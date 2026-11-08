import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Подключаем твои модули
import ai_chat
import rpg_game

# Безопасно получаем токен из настроек Railway
TOKEN = os.getenv("TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню с кнопками"""
    keyboard = [
        ["🤖 ИИ Чат", "🎮 RPG Игра"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я твой многофункциональный бот. Выбери режим ниже:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Распределение сообщений от пользователя"""
    text = update.message.text
    user_name = update.message.from_user.first_name or "Путешественник"

    if text == "🤖 ИИ Чат":
        await update.message.reply_text(
            "Режим ИИ активирован! Напиши свой вопрос."
        )
    elif text == "🎮 RPG Игра":
        # При первом нажатии на кнопку RPG автоматически запускаем сброс/старт игры
        response = await rpg_game.handle_rpg_action("/start_rpg", user_name=user_name)
        await update.message.reply_text(response, parse_mode="Markdown")
        
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
  
