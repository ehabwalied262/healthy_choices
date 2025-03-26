import os
import sqlite3
import psycopg2
from datetime import datetime
from config import DATABASE_NAME

# تحديد نوع قاعدة البيانات بناءً على المتغيرات البيئية
USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"
DATABASE_URL = os.getenv("POSTGRES_URL")
if DATABASE_URL and "sslmode" not in DATABASE_URL:
    DATABASE_URL = f"{DATABASE_URL}?sslmode=require"

def init_db():
    try:
        if USE_POSTGRES:
            # استخدام PostgreSQL لو كنت على Vercel
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
        else:
            # استخدام SQLite لو كنت على جهازك المحلي
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
        
        # إنشاء جدول users مع intro_index
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                language TEXT DEFAULT 'ar',
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_topic TEXT DEFAULT NULL,
                advice_index INTEGER DEFAULT 0,
                intro_index INTEGER DEFAULT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_text TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def log_message(user_id, message_text):
    try:
        if USE_POSTGRES:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO message_logs (user_id, message_text) VALUES (%s, %s)", (user_id, message_text))
        else:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO message_logs (user_id, message_text) VALUES (?, ?)", (user_id, message_text))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging message: {e}")

def update_user(user_id, username, language='ar', current_topic=None, advice_index=0, intro_index=None):
    try:
        if USE_POSTGRES:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, username, language, current_topic, advice_index, intro_index)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET username = %s, language = %s, current_topic = %s, advice_index = %s, intro_index = %s
            ''', (user_id, username, language, current_topic, advice_index, intro_index,
                  username, language, current_topic, advice_index, intro_index))
        else:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, language, current_topic, advice_index, intro_index)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, language, current_topic, advice_index, intro_index))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating user: {e}")

def get_user_state(user_id):
    try:
        if USE_POSTGRES:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT current_topic, advice_index, intro_index FROM users WHERE user_id = %s", (user_id,))
        else:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT current_topic, advice_index, intro_index FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result if result else (None, 0, None)
    except Exception as e:
        print(f"Error getting user state: {e}")
        return (None, 0, None)