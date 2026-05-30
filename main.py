import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
from aiohttp import web

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
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_text}]
            )
        )
        ai_response = response.choices.message.content
        await update.message.reply_text(ai_response)
    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")

# Фейковый веб-сервер для обмана Render
async def handle_ping(request):
    return web.Response(text="Bot is alive!")

async def start_fake_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Фейковый веб-сервер запущен на порту {port}")

async def main():
    if not TOKEN:
        logging.error("Ошибка: Переменная TELEGRAM_BOT_TOKEN не задана!")
        return

    # Запускаем веб-сервер, чтобы Render не ругался на порты
    await start_fake_server()

    # Настраиваем и запускаем телеграм-бота
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    await app.initialize()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    await app.start()
    
    logging.info("Бот успешно запущен и слушает Telegram...")
    
    # Бесконечный цикл удержания процесса активным
    while True:
        await asyncio.sleep(3600)

if name == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
