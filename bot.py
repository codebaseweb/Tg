import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import ai_chat

TOKEN = os.getenv("TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое приветствие с кнопкой меню"""
    keyboard = [
        ["🐾 Поболтать с Андрюшей"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я на связи, мур-мур 😊",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Распределение сообщений"""
    text = update.message.text
    
    if text == "🐾 Поболтать с Андрюшей":
        await update.message.reply_text("Я тут, солнышко! Чего нового? 🐾")
    else:
        # ВСЕ ОСТАЛЬНЫЕ СООБЩЕНИЯ (обычный текст) отправляются Андрюше
        response = await ai_chat.get_friend_response(text)
        await update.message.reply_text(response)

def main():
    if not TOKEN:
        print("Ошибка: Токен Telegram не найден!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен и готов мурчать!")
    application.run_polling()

if __name__ == "__main__":
    main()

