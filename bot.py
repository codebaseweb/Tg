import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import rpg_game
from telegram.ext import CallbackQueryHandler

import ai_chat

TOKEN = os.getenv("TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое приветствие с кнопкой меню"""
    keyboard = [
    ["🐾 Поболтать с Андрюшей", "🎮 RPG Игра"]
]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я на связи, мур-мур 😊",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_name = update.message.from_user.first_name or "Странник"

    if text == "🎮 RPG Игра":
        text_message, markup = await rpg_game.handle_rpg_action("start_rpg", user_name)
        await update.message.reply_text(text_message, reply_markup=markup, parse_mode="Markdown")
    elif text == "🐾 Поболтать с Андрюшей":
        await update.message.reply_text("Я тут, солнышко! Чего нового? 🐾")
    else:
        response = await ai_chat.get_friend_response(text)
        await update.message.reply_text(response)

async def game_inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_name = query.from_user.first_name or "Странник"

    text_message, markup = await rpg_game.handle_rpg_action(query.data, user_name)
    await query.edit_message_text(text=text_message, reply_markup=markup, parse_mode="Markdown")



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
    application.add_handler(CallbackQueryHandler(game_inline_handler))

    main()

