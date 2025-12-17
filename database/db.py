# database/db.py

import os
import sqlite3
import psycopg2
from datetime import datetime
from typing import Optional, Dict, Any

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_DB_PATH = "database/artbazar.db"


# =========================
# CONNECTIONS
# =========================

def is_postgres() -> bool:
    return bool(DATABASE_URL)


def get_db_connection():
    """КАНОНИЧНАЯ функция, ожидается owner_stats.py"""
    if is_postgres():
        return psycopg2.connect(DATABASE_URL)
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    return sqlite3.connect(SQLITE_DB_PATH)


# алиас для совместимости
get_connection = get_db_connection


# =========================
# USERS
# =========================

def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if is_postgres():
            cur.execute(
                """
                SELECT user_id, telegram_id, username, first_name, last_name,
                       role, premium_until, is_premium
                FROM users
                WHERE telegram_id = %s
                """,
                (telegram_id,),
            )
        else:
            cur.execute(
                """
                SELECT telegram_id, username, role, is_premium
                FROM users
                WHERE telegram_id = ?
                """,
                (telegram_id,),
            )

        row = cur.fetchone()
        if not row:
            return None

        if is_postgres():
            return {
                "user_id": row[0],
                "telegram_id": row[1],
                "username": row[2],
                "first_name": row[3],
                "last_name": row[4],
                "role": row[5],
                "premium_until": row[6],
                "is_premium": row[7],
            }

        return {
            "telegram_id": row[0],
            "username": row[1],
            "role": row[2],
            "is_premium": bool(row[3]),
        }

    finally:
        conn.close()


def ensure_user_exists(
    telegram_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    language: str = "ru",
):
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        if is_postgres():
            cur.execute(
                "SELECT user_id FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
            exists = cur.fetchone()

            if exists:
                cur.execute(
                    """
                    UPDATE users
                    SET username = %s,
                        first_name = %s,
                        last_name = %s
                    WHERE telegram_id = %s
                    """,
                    (username, first_name, last_name, telegram_id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO users (
                        user_id,
                        telegram_id,
                        username,
                        first_name,
                        last_name,
                        role,
                        language,
                        is_premium
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        telegram_id,   # user_id = telegram_id (канон)
                        telegram_id,
                        username,
                        first_name,
                        last_name,
                        "user",
                        language,
                        False,
                    ),
                )
        else:
            cur.execute(
                "SELECT telegram_id FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            if not cur.fetchone():
                cur.execute(
                    """
                    INSERT INTO users (telegram_id, username, role, is_premium)
                    VALUES (?, ?, ?, ?)
                    """,
                    (telegram_id, username, "user", 0),
                )

        conn.commit()
    finally:
        conn.close()


def get_user_role(telegram_id: int) -> str:
    user = get_user(telegram_id)
    return user["role"] if user else "user"


def set_role_by_telegram_id(telegram_id: int, role: str):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if is_postgres():
            cur.execute(
                "UPDATE users SET role = %s WHERE telegram_id = %s",
                (role, telegram_id),
            )
        else:
            cur.execute(
                "UPDATE users SET role = ? WHERE telegram_id = ?",
                (role, telegram_id),
            )
        conn.commit()
    finally:
        conn.close()


# алиас для совместимости
def set_user_role(telegram_id: int, role: str):
    set_role_by_telegram_id(telegram_id, role)


def is_user_premium(telegram_id: int) -> bool:
    user = get_user(telegram_id)
    return bool(user and user.get("is_premium"))
