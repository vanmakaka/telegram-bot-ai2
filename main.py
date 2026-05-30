import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Инициализация клиентов
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я ваш ИИ-ассистент. Задайте мне любой вопрос.")

async def handle_message(update: Update, context):
    user_text = update.message.text
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_text}]
        )
        ai_response = response.choices.message.content
        await update.message.reply_text(ai_response)
    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")

async def main():
    if not TOKEN:
        logging.error("Ошибка: Переменная TELEGRAM_BOT_TOKEN не задана!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Инициализируем и запускаем приложение корректно для фонового процесса
    await app.initialize()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    await app.start()
    
    logging.info("Бот успешно запущен и работает...")
    
    # Держим процесс активным, чтобы Render не закрывал его
    while True:
        await asyncio.sleep(3600)

if name == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
