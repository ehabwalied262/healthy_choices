import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from handlers import handle_start, handle_show_topics, handle_topic_selection, handle_next_advice, handle_list
from database import init_db
from config import API_ID, API_HASH, BOT_TOKEN

# بيانات البوت من config.py
API_ID = int(API_ID)  # بنحول API_ID إلى int لأنه في config.py هو string
API_HASH = API_HASH
BOT_TOKEN = BOT_TOKEN

# إنشاء البوت
bot = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# Register handlers
bot.on_message(filters.command("start"))(handle_start)
bot.on_callback_query(filters.regex("show_topics"))(handle_show_topics)
bot.on_callback_query(filters.regex(r"topic_(.+)"))(handle_topic_selection)
bot.on_callback_query(filters.regex(r"(intro|next_advice)_(.+)_(\d+)"))(handle_next_advice)
bot.on_message(filters.command("list"))(handle_list)

# إعداد Webhook لـ Vercel
async def handle_webhook(request):
    try:
        update = await request.json()
        print(f"Received update: {update}")
        await bot.handle_updates([update])
        return web.Response(text="OK")
    except Exception as e:
        print(f"Error handling webhook: {e}")
        return web.Response(text="Error", status=500)

# إعداد السيرفر
web_app = web.Application()
web_app.router.add_post(f"/webhook/{BOT_TOKEN}", handle_webhook)

# تشغيل البوت مع Webhook
async def start_bot():
    # احصل على الـ URL بتاع Vercel
    vercel_url = os.getenv("VERCEL_URL")
    if not vercel_url:
        vercel_url = "https://healthy-choices.vercel.app"  # استبدلها بالـ URL بتاعك
    
    # إعداد الـ Webhook
    webhook_url = f"{vercel_url}/webhook/{BOT_TOKEN}"
    print(f"Setting webhook to {webhook_url}")

    # التحقق من حالة الـ Webhook الحالية
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != webhook_url:
        await bot.set_webhook(url=webhook_url)
        print("Webhook set successfully!")
    else:
        print("Webhook already set to this URL!")

    # بدء تشغيل البوت
    await bot.start()
    print("Bot started successfully!")

# تشغيل السيرفر والبوت معًا
if __name__ == "__main__":
    print("Initializing database...")
    try:
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        raise
    
    print("Starting the program...")
    # تشغيل البوت والسيرفر معًا
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    web.run_app(web_app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))