# -*- coding: utf-8 -*-

"""
services/premium_checker.py

КАНОНИЧЕСКИЙ СЛОЙ PREMIUM

Здесь ДВЕ ответственности, разведённые явно:

1. Premium Guard
   - синхронная проверка: есть ли у пользователя Premium СЕЙЧАС
   - используется UI / handlers
   - single source of truth = БД

2. Premium Lifecycle
   - фоновые проверки
   - уведомления
   - авто-отключение истёкшего Premium
"""

from datetime import datetime, timedelta
from telegram import Bot

from config import BOT_TOKEN

# БД — ЕДИНСТВЕННЫЙ ИСТОЧНИК ИСТИНЫ
from database.db import is_user_premium
from database.models import (
    get_all_premium_users,
    disable_expired_premium,
)


# ==================================================
# PREMIUM GUARD (UI / HANDLERS)
# ==================================================

def is_premium_user(user_id: int) -> bool:
    """
    Каноническая проверка Premium-статуса пользователя.

    Используется:
    - handlers/profile.py
    - экспорт PDF / Excel
    - любые Premium-ограничения в UI

    ВАЖНО:
    - синхронная
    - не содержит бизнес-логики
    - просто прокси к БД
    """
    try:
        return bool(is_user_premium(user_id))
    except Exception:
        return False


# ==================================================
# PREMIUM LIFECYCLE (CRON / BACKGROUND)
# ==================================================

async def check_premium_expiration():
    """
    Фоновая задача.

    Делает:
    - уведомление за 3 дня до окончания Premium
    - уведомление за 1 день
    - авто-отключение истёкшего Premium

    НЕ используется напрямую в UI.
    """

    bot = Bot(BOT_TOKEN)
    users = get_all_premium_users()
    now = datetime.utcnow()

    for user_id, username, premium_until in users:
        if not premium_until:
            continue

        try:
            expiry = datetime.fromisoformat(premium_until)
        except Exception:
            continue

        delta = expiry - now

        # Уведомление за 3 дня
        if timedelta(days=3) >= delta > timedelta(days=2):
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        "⚠ *Ваш Premium истекает через 3 дня!*\n\n"
                        "Продлите доступ, чтобы сохранить историю и экспорт отчётов."
                    ),
                    parse_mode="Markdown",
                )
            except Exception:
                pass

        # Уведомление за 1 день
        elif timedelta(days=1) >= delta > timedelta(hours=23):
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        "⏳ *Ваш Premium истекает завтра!*\n\n"
                        "Продлите, чтобы не потерять доступ к PDF и Excel отчётам."
                    ),
                    parse_mode="Markdown",
                )
            except Exception:
                pass

    # Авто-отключение истёкших
    disable_expired_premium()
