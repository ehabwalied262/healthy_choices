# Main entry point for the bot
from pyrogram import Client, filters
from config import BOT_TOKEN, API_ID, API_HASH, GEMINI_API_KEY
from handlers import handle_start, handle_show_topics, handle_topic_selection, handle_general_message, handle_next_advice, handle_list
from database import init_db , init_requests_db
import google.generativeai as genai
import asyncio


# Configure Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    # Handle configuration error appropriately


# Initialize the bot with Pyrogram
bot = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,

)

# Register handlers
# 1. Register specific command handlers FIRST
bot.on_message(filters.command("start"))(handle_start)
bot.on_message(filters.command("list"))(handle_list)

# 2. Register other specific message handlers if any (none shown in your snippet besides commands)
# Example: bot.on_message(filters.regex("some_pattern"))(some_handler)

# 3. Register callback query handlers (these are different from message handlers, their order relative to messages doesn't matter)
bot.on_callback_query(filters.regex("show_topics"))(handle_show_topics)
bot.on_callback_query(filters.regex(r"topic_(.+)"))(handle_topic_selection)
bot.on_callback_query(filters.regex(r"(intro|next_advice)_(.+)_(\d+)"))(handle_next_advice)

# 4. Register the general text handler LAST
# This handler will catch any text message that wasn't caught by the specific handlers above it.
bot.on_message(filters.text)(handle_general_message)

# Initialize database before starting the bot
print("Initializing database...")
init_db()
print("Database initialized.")
init_requests_db()  # For API requests          

# Run the bot
if __name__ == "__main__":
    print("Starting the program...")
    bot.run()
    # print("Program finished.")