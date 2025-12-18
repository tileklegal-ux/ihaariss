# database/db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import closing
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# =========================
# USERS
# =========================

def ensure_user_exists(
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
):
    with closing(get_connection()) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (telegram_id, username, first_name, last_name, role)
                VALUES (%s, %s, %s, %s, 'user')
                ON CONFLICT (telegram_id) DO UPDATE
                SET username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name
            """, (telegram_id, username, first_name, last_name))
            conn.commit()


def get_user_role(telegram_id: int) -> str:
    with closing(get_connection()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT role FROM users WHERE telegram_id = %s",
                (telegram_id,)
            )
            row = cur.fetchone()
            return row["role"] if row else "user"


def set_user_role(telegram_id: int, role: str):
    with closing(get_connection()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET role = %s WHERE telegram_id = %s",
                (role, telegram_id)
            )
            conn.commit()


# =========================
# PREMIUM
# =========================

def is_user_premium(telegram_id: int) -> bool:
    with closing(get_connection()) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT premium_until
                FROM users
                WHERE telegram_id = %s
            """, (telegram_id,))
            row = cur.fetchone()
            return bool(row and row["premium_until"] and row["premium_until"] > datetime.utcnow())


def grant_premium(telegram_id: int, until: datetime):
    with closing(get_connection()) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET is_premium = TRUE,
                    premium_until = %s
                WHERE telegram_id = %s
            """, (until, telegram_id))
            conn.commit()
