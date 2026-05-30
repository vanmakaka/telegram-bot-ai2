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
        # Используем асинхронный запуск в потоке, чтобы синхронный OpenAI клиент не вешал бота
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_text}]
            )
        )
        ai_response = response.choices[0].message.content
        await update.message.reply_text(ai_response)
    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")

def main():
    if not TOKEN:
        logging.error("Ошибка: Переменная TELEGRAM_BOT_TOKEN не задана!")
        return

    # Стандартный и самый надежный запуск бота для Render
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("Бот успешно запущен и начинает опрос серверов Telegram...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if name == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
