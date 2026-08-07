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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS contents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_id TEXT UNIQUE,
        content_type TEXT,
        file_id TEXT,
        created_date TEXT
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


def add_content(content_id, content_type, file_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO contents 
        (content_id, content_type, file_id, created_date)
        VALUES (?, ?, ?, ?)
        """,
        (
            content_id,
            content_type,
            file_id,
            datetime.now().strftime("%Y-%m-%d")
        )
    )

    conn.commit()
    conn.close()


def get_content(content_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT content_type, file_id FROM contents WHERE content_id=?",
        (content_id,)
    )

    result = cur.fetchone()

    conn.close()

    return result


def get_last_content_number():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM contents")

    result = cur.fetchone()[0]

    conn.close()

    return result + 1


def get_all_users():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users")

    users = cur.fetchall()

    conn.close()

    return [user[0] for user in users]

