import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import ai_chat  # наш мурчащий Андрюша
import rpg_game # твой новый файл с игрой

TOKEN = os.getenv("TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню с кнопками"""
    keyboard = [
        ["🐾 Поболтать с Андрюшей", "🎮 RPG Игра"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Выбери, куда отправимся:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_name = update.message.from_user.first_name or "Странник"
from telegram.ext import CallbackQueryHandler
# ... (остальные импорты bot.py, токен, создание application)

# Отдельная функция для обработки кликов по инлайн-кнопкам в игре
async def game_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Обязательно подтверждаем нажатие, чтобы убрать крутящиеся «часики» на кнопке
    
    # Передаем скрытый код кнопки (например, "go_cave") в файл игры
    text_message, markup = rpg_game.handle_callback(query.data)
    
    # Заменяем старое сообщение на новое с обновленными статами и кнопками
    await query.edit_message_text(text=text_message, reply_markup=markup, parse_mode="Markdown")

# В функции main() обязательно регистрируем этот обработчик:
application.add_handler(CallbackQueryHandler(game_button_handler))

    # Если нажата кнопка RPG игры
    if text == "🎮 RPG Игра":
        # Вызываем функцию старта игры из файла rpg_game.py
        response = rpg_game.start_game(user_name)
        await update.message.reply_text(response, parse_mode="Markdown")
        
    elif text == "🐾 Поболтать с Андрюшей":
        await update.message.reply_text("Андрюша на связи, мур-мур! Чего хотел? 😊")
        
    else:
        # Всё остальное отправляем Андрюше
        response = await ai_chat.get_friend_response(text)
        await update.message.reply_text(response)

def main():
    if not TOKEN:
        print("Ошибка: Токен не найден!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
