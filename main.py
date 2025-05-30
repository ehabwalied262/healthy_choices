# Main entry point for the bot
from pyrogram import Client, filters
from config import BOT_TOKEN, API_ID, API_HASH, GEMINI_API_KEY
from handlers import (
    handle_start, handle_show_topics, handle_topic_selection, handle_general_message,
    handle_next_advice, handle_list, handle_my_nutritionist, handle_my_info,
    handle_nutritionist_start, handle_nutritionist_has_condition, handle_nutritionist_condition,
    handle_nutritionist_text_input, handle_nutritionist_goal, handle_food_restrictions,
    handle_help, handle_about, handle_menu
)
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
bot.on_message(filters.command("help"))(handle_help)
bot.on_message(filters.command("about"))(handle_about)
bot.on_message(filters.command("my_nutritionist"))(handle_my_nutritionist)
bot.on_message(filters.command("my_info"))(handle_my_info)
bot.on_message(filters.command("menu"))(handle_menu)

# 2. Register callback query handlers
bot.on_callback_query(filters.regex("show_topics"))(handle_show_topics)
bot.on_callback_query(filters.regex(r"topic_(.+)"))(handle_topic_selection)
bot.on_callback_query(filters.regex(r"(intro|next_advice)_(.+)_(\d+)"))(handle_next_advice)
bot.on_callback_query(filters.regex(r"^nutritionist_start$"))(handle_nutritionist_start)
bot.on_callback_query(filters.regex(r"^nutritionist_has_condition_"))(handle_nutritionist_has_condition)
bot.on_callback_query(filters.regex(r"^nutritionist_condition_"))(handle_nutritionist_condition)
bot.on_callback_query(filters.regex(r"^nutritionist_goal_"))(handle_nutritionist_goal)

# 3. Register text input handlers for nutritionist questions
bot.on_message(filters.text & ~filters.command(["start", "list", "help", "about", "my_nutritionist", "my_info", "menu"]))(handle_nutritionist_text_input)
bot.on_message(filters.text & ~filters.command(["start", "list", "help", "about", "my_nutritionist", "my_info", "menu"]))(handle_food_restrictions)

# 4. Register the general text handler LAST
bot.on_message(filters.text & ~filters.command(["start", "list", "help", "about", "my_nutritionist", "my_info", "menu"]))(handle_general_message)

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