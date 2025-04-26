import sqlite3
from config import DATABASE_NAME
from datetime import date
import json

def init_db():
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

def init_requests_db():
    conn = sqlite3.connect('requests.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS api_requests
                     (date TEXT PRIMARY KEY, request_count INTEGER)''')
    conn.commit()
    conn.close()

def log_message(user_id, message_text):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO message_logs (user_id, message_text) VALUES (?, ?)", (user_id, message_text))
    conn.commit()
    conn.close()

def update_user(user_id, username, **kwargs):
    # افتح قاعدة البيانات (مثلاً SQLite)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # إنشاء جدول لو مش موجود
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                   (user_id TEXT PRIMARY KEY, username TEXT, data TEXT)''')
    # تحويل kwargs لـ JSON عشان يتخزن كـ string
    data = json.dumps(kwargs)
    # تحديث بيانات المستخدم
    cursor.execute("INSERT OR REPLACE INTO users (user_id, username, data) VALUES (?, ?, ?)",
                  (str(user_id), username, data))
    conn.commit()
    conn.close()

def get_user_state(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM users WHERE user_id = ?", (str(user_id),))
    result = cursor.fetchone()
    conn.close()
    if result:
        return json.loads(result[0])  # إرجاع البيانات كـ dictionary
    return {}

def get_all_users():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def get_request_count():
    today = str(date.today())
    conn = sqlite3.connect('requests.db')
    cursor = conn.cursor()
    cursor.execute('SELECT request_count FROM api_requests WHERE date = ?', (today,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def increment_request_count():
    today = str(date.today())
    conn = sqlite3.connect('requests.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO api_requests (date, request_count) VALUES (?, COALESCE((SELECT request_count FROM api_requests WHERE date = ?), 0) + 1)',
                  (today, today))
    conn.commit()
    conn.close()