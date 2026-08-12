import sqlite3
from datetime import datetime


DB = "users.db"


def get_connection():
    return sqlite3.connect(DB)


def init_db():

    conn = get_connection()
    cur = conn.cursor()

    # Users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        join_date TEXT
    )
    """)

    # Contents
    cur.execute("""
    CREATE TABLE IF NOT EXISTS contents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_id TEXT UNIQUE,
        content_type TEXT,
        file_id TEXT,
        category TEXT,
        caption TEXT DEFAULT '',
        views INTEGER DEFAULT 0,
        created_date TEXT
    )
    """)

    # Collection items
    cur.execute("""
    CREATE TABLE IF NOT EXISTS collections (
        collection_id TEXT,
        content_id TEXT,
        position INTEGER,
        PRIMARY KEY (collection_id, content_id)
    )
    """)

    # Migration برای دیتابیس‌های قدیمی
    cur.execute("PRAGMA table_info(contents)")
    columns = [
        row[1]
        for row in cur.fetchall()
    ]

    if "caption" not in columns:
        cur.execute("""
        ALTER TABLE contents
        ADD COLUMN caption TEXT DEFAULT ''
        """)

    conn.commit()
    conn.close()


# ==========================================
# USERS
# ==========================================

def add_user(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, join_date)
        VALUES (?, ?)
        """,
        (
            user_id,
            datetime.now().strftime("%Y-%m-%d")
        )
    )

    conn.commit()
    conn.close()


def get_total_users():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM users"
    )

    result = cur.fetchone()[0]

    conn.close()

    return result


def get_today_users():

    conn = get_connection()
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE join_date=?
        """,
        (today,)
    )

    result = cur.fetchone()[0]

    conn.close()

    return result


def get_all_users():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id FROM users"
    )

    users = cur.fetchall()

    conn.close()

    return [
        user[0]
        for user in users
    ]


# ==========================================
# CONTENT
# ==========================================

def add_content(
    content_id,
    content_type,
    file_id,
    category,
    caption=""
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO contents
        (
            content_id,
            content_type,
            file_id,
            category,
            caption,
            created_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            content_id,
            content_type,
            file_id,
            category,
            caption,
            datetime.now().strftime("%Y-%m-%d")
        )
    )

    conn.commit()
    conn.close()


def get_content(content_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT content_type, file_id, caption
        FROM contents
        WHERE content_id=?
        """,
        (content_id,)
    )

    result = cur.fetchone()

    if result:

        cur.execute(
            """
            UPDATE contents
            SET views = views + 1
            WHERE content_id=?
            """,
            (content_id,)
        )

        conn.commit()

    conn.close()

    return result


def get_last_content_number():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM contents"
    )

    result = cur.fetchone()[0]

    conn.close()

    return result + 1


def get_total_contents():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM contents"
    )

    result = cur.fetchone()[0]

    conn.close()

    return result


def get_total_views():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COALESCE(SUM(views), 0) FROM contents"
    )

    result = cur.fetchone()[0]

    conn.close()

    return result


# ==========================================
# COLLECTIONS
# ==========================================

def create_collection(collection_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM collections
        WHERE collection_id=?
        """,
        (collection_id,)
    )

    conn.commit()
    conn.close()


def add_to_collection(
    collection_id,
    content_id,
    position
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO collections
        (
            collection_id,
            content_id,
            position
        )
        VALUES (?, ?, ?)
        """,
        (
            collection_id,
            content_id,
            position
        )
    )

    conn.commit()
    conn.close()


def get_collection(collection_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT content_id
        FROM collections
        WHERE collection_id=?
        ORDER BY position ASC
        """,
        (collection_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return [
        row[0]
        for row in rows
    ]
