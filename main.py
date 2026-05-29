# main.py — Telegram бот с ИИ-ответами
# Установите библиотеки: python-telegram-bot, openai, python-dotenv

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Настройка логирования (чтобы видеть ошибки)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Инициализация клиентов
# Ключи берутся из Secrets (не из кода!)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я ИИ-помощник.\n"
        "Напиши мне любой вопрос — я отвечу с помощью GPT-4o-mini.\n"
        "Команды:\n"
        "/start — начать заново\n"
        "/help — справка"
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Справка:\n"
        "• Просто напиши вопрос — я отвечу\n"
        "• Я помню контекст беседы (последние 5 сообщений)\n"
        "• Если ответ некорректный — переформулируй вопрос"
    )

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.message.from_user.id
    
    # Логгируем запрос
    logging.info(f"User {user_id}: {user_text}")
    
    try:
        # Запрос к OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты полезный помощник. Отвечай кратко и по делу."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=500
        )
        
        ai_reply = response.choices[0].message.content
        
        # Отправляем ответ
        await update.message.reply_text(ai_reply)
        logging.info(f"AI reply sent to user {user_id}")
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")

# Главная функция
def main():
    # Создаём приложение
    app = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logging.info("Starting bot...")
    app.run_polling(drop_pending_updates=True)

# Запуск
if __name__ == "__main__":
    main()
