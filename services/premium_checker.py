# services/premium_checker.py
import logging
import os
from datetime import datetime, timedelta, timezone

from database.db import get_connection

logger = logging.getLogger(__name__)


def _is_postgres() -> bool:
    return bool(os.getenv("DATABASE_URL"))


def _ph() -> str:
    return "%s" if _is_postgres() else "?"


def _utcnow():
    return datetime.now(timezone.utc)


def _to_db_dt(dt: datetime):
    # Postgres принимает datetime; SQLite часто хранит строку — оставим dt, драйвер справится/преобразует.
    return dt


def _fetch_one_user(telegram_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = _ph()
        cur.execute(
            f"SELECT telegram_id, is_premium, premium_until FROM users WHERE telegram_id = {ph}",
            (telegram_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "telegram_id": row[0],
            "is_premium": bool(row[1]),
            "premium_until": row[2],
        }
    finally:
        conn.close()


def _update_premium_until(telegram_id: int, premium_until: datetime):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = _ph()
        if _is_postgres():
            cur.execute(
                f"""
                UPDATE users
                SET is_premium = TRUE,
                    premium_until = {ph}
                WHERE telegram_id = {ph}
                """,
                (_to_db_dt(premium_until), telegram_id),
            )
        else:
            cur.execute(
                f"""
                UPDATE users
                SET is_premium = 1,
                    premium_until = {ph}
                WHERE telegram_id = {ph}
                """,
                (_to_db_dt(premium_until), telegram_id),
            )
        conn.commit()
    finally:
        conn.close()


def _remove_premium_from_db(telegram_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = _ph()
        if _is_postgres():
            cur.execute(
                f"""
                UPDATE users
                SET is_premium = FALSE,
                    premium_until = NULL
                WHERE telegram_id = {ph}
                """,
                (telegram_id,),
            )
        else:
            cur.execute(
                f"""
                UPDATE users
                SET is_premium = 0,
                    premium_until = NULL
                WHERE telegram_id = {ph}
                """,
                (telegram_id,),
            )
        conn.commit()
    finally:
        conn.close()


def _disable_if_expired(telegram_id: int, premium_until) -> bool:
    if premium_until is None:
        return False

    now = _utcnow()

    # premium_until может прийти строкой из SQLite
    if isinstance(premium_until, str):
        try:
            premium_until = datetime.fromisoformat(premium_until.replace("Z", "+00:00"))
        except Exception:
            # если формат непонятен — считаем активным, чтобы не ломать UX
            return True

    # naive -> считаем UTC
    if isinstance(premium_until, datetime) and premium_until.tzinfo is None:
        premium_until = premium_until.replace(tzinfo=timezone.utc)

    if premium_until <= now:
        try:
            _remove_premium_from_db(telegram_id)
            logger.info(f"Premium отключён (истёк) telegram_id={telegram_id}")
        except Exception as e:
            logger.exception(f"Ошибка автоотключения премиума: {e}")
        return False

    return True


# -----------------------------
# PUBLIC: проверка премиума
# -----------------------------
def is_premium_user(telegram_id: int) -> bool:
    try:
        user = _fetch_one_user(telegram_id)
    except Exception as e:
        logger.exception(f"Ошибка получения юзера при проверке премиума: {e}")
        return False

    if not user:
        return False

    if not user.get("is_premium"):
        return False

    return _disable_if_expired(telegram_id, user.get("premium_until"))


# -----------------------------
# PUBLIC: выдать премиум
# -----------------------------
def set_premium(telegram_id: int, days: int = 30) -> bool:
    try:
        now = _utcnow()
        new_until = now + timedelta(days=int(days))
        _update_premium_until(telegram_id, new_until)
        logger.info(f"Premium выдан telegram_id={telegram_id} на {days} дней")
        return True
    except Exception as e:
        logger.exception(f"Ошибка выдачи премиума: {e}")
        return False


# -----------------------------
# PUBLIC: продлить премиум
# -----------------------------
def extend_premium(telegram_id: int, days: int) -> bool:
    try:
        user = _fetch_one_user(telegram_id)
        now = _utcnow()
        days = int(days)

        current = None
        if user and user.get("premium_until"):
            current = user["premium_until"]

        if isinstance(current, str):
            try:
                current = datetime.fromisoformat(current.replace("Z", "+00:00"))
            except Exception:
                current = None

        if isinstance(current, datetime) and current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)

        if current and current > now:
            new_until = current + timedelta(days=days)
        else:
            new_until = now + timedelta(days=days)

        _update_premium_until(telegram_id, new_until)
        logger.info(f"Premium продлён telegram_id={telegram_id} на {days} дней")
        return True
    except Exception as e:
        logger.exception(f"Ошибка продления премиума: {e}")
        return False


# -----------------------------
# PUBLIC: полностью снять премиум
# -----------------------------
def remove_premium(telegram_id: int) -> bool:
    try:
        _remove_premium_from_db(telegram_id)
        logger.info(f"Premium снят telegram_id={telegram_id}")
        return True
    except Exception as e:
        logger.exception(f"Ошибка снятия премиума: {e}")
        return False


# -----------------------------
# OPTIONAL: список тех, у кого скоро истекает
# -----------------------------
def get_users_with_expiring_premium(days_left: int = 3):
    try:
        now = _utcnow()
        deadline = now + timedelta(days=int(days_left))

        conn = get_connection()
        try:
            cur = conn.cursor()
            # Берём только premium=True
            if _is_postgres():
                cur.execute(
                    "SELECT telegram_id, premium_until FROM users WHERE is_premium = TRUE AND premium_until IS NOT NULL"
                )
            else:
                cur.execute(
                    "SELECT telegram_id, premium_until FROM users WHERE is_premium = 1 AND premium_until IS NOT NULL"
                )
            rows = cur.fetchall() or []
        finally:
            conn.close()

        result = []
        for telegram_id, premium_until in rows:
            _until = premium_until
            if isinstance(_until, str):
                try:
                    _until = datetime.fromisoformat(_until.replace("Z", "+00:00"))
                except Exception:
                    continue
            if isinstance(_until, datetime) and _until.tzinfo is None:
                _until = _until.replace(tzinfo=timezone.utc)

            if _until and now < _until <= deadline:
                result.append({"telegram_id": telegram_id, "premium_until": _until})

        return result
    except Exception as e:
        logger.exception(f"Ошибка получения списка истекающих премиумов: {e}")
        return []
