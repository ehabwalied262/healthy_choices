import sqlite3
from config import DATABASE_NAME

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

def log_message(user_id, message_text):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO message_logs (user_id, message_text) VALUES (?, ?)", (user_id, message_text))
    conn.commit()
    conn.close()

def update_user(user_id, username, language='ar', current_topic=None, advice_index=0, intro_index=None):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # تحديث أو إضافة بيانات المستخدم مع intro_index
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, language, current_topic, advice_index, intro_index)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, language, current_topic, advice_index, intro_index))
    
    conn.commit()
    conn.close()

def get_user_state(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT current_topic, advice_index, intro_index FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result if result else (None, 0, None)