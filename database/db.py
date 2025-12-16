# database/db.py
import os
from datetime import datetime, timedelta

import psycopg2

# Railway автоматически прокидывает DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")


# ==================================================
# CONNECTION
# ==================================================

def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set (PostgreSQL is required in production)")
    return psycopg2.connect(DATABASE_URL)


# ==================================================
# INIT / SCHEMA
# ==================================================

def init_db():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                role TEXT DEFAULT 'user',
                is_premium BOOLEAN DEFAULT FALSE,
                premium_until TIMESTAMP,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            """
        )

        now = datetime.utcnow()
        cur.execute("UPDATE users SET created_at = COALESCE(created_at, %s)", (now,))
        cur.execute("UPDATE users SET updated_at = COALESCE(updated_at, %s)", (now,))

        conn.commit()
    finally:
        conn.close()


# ==================================================
# USERS
# ==================================================

def create_or_update_user(telegram_id: int, username: str, first_name: str):
    init_db()

    username = (username or "").lstrip("@")
    first_name = first_name or ""
    now = datetime.utcnow()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT telegram_id FROM users WHERE telegram_id = %s",
            (telegram_id,),
        )
        exists = cur.fetchone() is not None

        if exists:
            cur.execute(
                """
                UPDATE users
                SET username = %s,
                    first_name = %s,
                    updated_at = %s
                WHERE telegram_id = %s
                """,
                (username, first_name, now, telegram_id),
            )
        else:
            # ⛔ ВАЖНО: роль по умолчанию ТОЛЬКО 'user'
            cur.execute(
                """
                INSERT INTO users
                (telegram_id, username, first_name, role, is_premium, created_at, updated_at)
                VALUES (%s, %s, %s, 'user', FALSE, %s, %s)
                """,
                (telegram_id, username, first_name, now, now),
            )

        conn.commit()
    finally:
        conn.close()


def get_user_role(telegram_id: int) -> str:
    init_db()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT role FROM users WHERE telegram_id = %s",
            (telegram_id,),
        )
        row = cur.fetchone()
        return row[0] if row else "user"
    finally:
        conn.close()


def set_role_by_telegram_id(telegram_id: int, role: str) -> bool:
    init_db()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE users
            SET role = %s,
                updated_at = %s
            WHERE telegram_id = %s
            """,
            (role, datetime.utcnow(), telegram_id),
        )
        ok = cur.rowcount > 0
        conn.commit()
        return ok
    finally:
        conn.close()


def get_user_by_username(username: str):
    init_db()

    username = (username or "").lstrip("@").lower()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT telegram_id, username, role
            FROM users
            WHERE LOWER(username) = %s
            """,
            (username,),
        )
        row = cur.fetchone()
        if not row:
            return None

        return {
            "telegram_id": row[0],
            "username": row[1],
            "role": row[2],
        }
    finally:
        conn.close()


# ==================================================
# PREMIUM
# ==================================================

def set_premium_by_telegram_id(telegram_id: int, days: int) -> bool:
    init_db()

    now = datetime.utcnow()
    premium_until = now + timedelta(days=days)

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE users
            SET is_premium = TRUE,
                premium_until = %s,
                updated_at = %s
            WHERE telegram_id = %s
            """,
            (premium_until, now, telegram_id),
        )
        ok = cur.rowcount > 0
        conn.commit()
        return ok
    finally:
        conn.close()


def is_user_premium(telegram_id: int) -> bool:
    init_db()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT is_premium, premium_until
            FROM users
            WHERE telegram_id = %s
            """,
            (telegram_id,),
        )
        row = cur.fetchone()
        if not row:
            return False

        is_premium, premium_until = row
        if not is_premium:
            return False

        if premium_until:
            return premium_until > datetime.utcnow()

        return True
    finally:
        conn.close()


# ==================================================
# STATS
# ==================================================

def get_stats():
    init_db()

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        stats = {}
        for role in ("user", "manager", "owner"):
            cur.execute("SELECT COUNT(*) FROM users WHERE role = %s", (role,))
            stats[role] = int(cur.fetchone()[0])

        cur.execute("SELECT COUNT(*) FROM users WHERE is_premium = TRUE")
        stats["premium"] = int(cur.fetchone()[0])

        return stats
    finally:
        conn.close()
