import logging
from datetime import datetime, timedelta, timezone
from database.db import (
    get_user,
    update_premium_until,
    remove_premium_from_db,
    get_all_premium_users,
)

logger = logging.getLogger(__name__)


def _disable_if_expired(telegram_id: int, premium_until) -> bool:
    if premium_until is None:
        return False

    now = datetime.now(timezone.utc)

    if isinstance(premium_until, datetime) and premium_until.tzinfo is None:
        premium_until = premium_until.replace(tzinfo=timezone.utc)

    if premium_until <= now:
        remove_premium_from_db(telegram_id)
        return False

    return True


def is_premium_user(telegram_id: int) -> bool:
    user = get_user(telegram_id)
    if not user:
        return False

    return _disable_if_expired(
        telegram_id,
        user.get("premium_until")
    )


def set_premium(telegram_id: int, days: int = 30) -> bool:
    try:
        now = datetime.now(timezone.utc)
        update_premium_until(telegram_id, now + timedelta(days=days))
        return True
    except Exception as e:
        logger.exception(e)
        return False


def extend_premium(telegram_id: int, days: int) -> bool:
    try:
        user = get_user(telegram_id)
        now = datetime.now(timezone.utc)

        base = user["premium_until"] if user and user.get("premium_until") else now
        if base < now:
            base = now

        update_premium_until(telegram_id, base + timedelta(days=days))
        return True
    except Exception as e:
        logger.exception(e)
        return False


def remove_premium(telegram_id: int) -> bool:
    try:
        remove_premium_from_db(telegram_id)
        return True
    except Exception as e:
        logger.exception(e)
        return False


def get_users_with_expiring_premium(days_left: int = 3):
    now = datetime.now(timezone.utc)
    deadline = now + timedelta(days=days_left)

    result = []
    for u in get_all_premium_users():
        until = u.get("premium_until")
        if until and now < until <= deadline:
            result.append(u)
    return result
