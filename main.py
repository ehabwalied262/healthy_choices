# Main entry point for the bot
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from handlers import handle_start, handle_show_topics, handle_topic_selection, handle_next_advice, handle_list
from database import init_db

# Initialize the bot with Pyrogram
bot = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    
)

# Register handlers directly in main.py
bot.on_message(filters.command("start"))(handle_start)
bot.on_callback_query(filters.regex("show_topics"))(handle_show_topics)
bot.on_callback_query(filters.regex(r"topic_(.+)"))(handle_topic_selection)
bot.on_callback_query(filters.regex(r"(intro|next_advice)_(.+)_(\d+)"))(handle_next_advice)
bot.on_message(filters.command("list"))(handle_list)


# التعامل مع الأوامر الجديدة
@bot.on_message(filters.command("tweet"))
async def tweet_command(client, message):
    await message.reply_text("جاري تنفيذ أمر /tweet")

@bot.on_message(filters.command("settings"))
async def settings_command(client, message):
    await message.reply_text("جاري تنفيذ أمر /settings")

@bot.on_message(filters.command("privacy"))
async def privacy_command(client, message):
    await message.reply_text("جاري تنفيذ أمر /privacy")

@bot.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text("دي رسالة المساعدة!")


# Initialize database before starting the bot
print("Initializing database...")
init_db()
print("Database initialized.")

# Run the bot
if __name__ == "__main__":
    print("Starting the program...")
    bot.run()