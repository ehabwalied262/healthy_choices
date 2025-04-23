# Configuration file for storing constants and sensitive data
from dotenv import load_dotenv
import os

# load variables from .env
load_dotenv()

# Database configuration
DATABASE_NAME = os.getenv('DATABASE_NAME')

# API keys or other external service credentials (if needed)
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

# Bot token from BotFather on Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

