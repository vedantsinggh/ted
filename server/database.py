import sqlite3
from datetime import datetime

DB_NAME = "ted.db"

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Create Tasks Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            due_date TEXT,
            priority TEXT,
            created_at TEXT
        )
    ''')
    
    # Create Meetings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            meeting_time TEXT,
            participants TEXT,
            location TEXT,
            created_at TEXT
        )
    ''')
    
    # Create Reminders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            remind_at TEXT,
            repeat TEXT,
            created_at TEXT
        )
    ''')
    
    # Create Dynamic Info Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dynamic_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            value TEXT,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Example function to add dynamic info
def add_dynamic_info(key, value):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dynamic_info (key, value, created_at)
        VALUES (?, ?, ?)
    ''', (key, value, datetime.now().isoformat()))
    conn.commit()
    conn.close()
