import sqlite3
from datetime import datetime

DB = "users.db"


def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        join_date TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, join_date) VALUES (?, ?)",
        (user_id, datetime.now().strftime("%Y-%m-%d"))
    )

    conn.commit()
    conn.close()


def get_total_users():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    result = cur.fetchone()[0]

    conn.close()
    return result


def get_today_users():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute(
        "SELECT COUNT(*) FROM users WHERE join_date=?",
        (today,)
    )

    result = cur.fetchone()[0]

    conn.close()
    return result
