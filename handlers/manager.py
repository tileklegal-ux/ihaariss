# handlers/manager.py

from datetime import datetime, timedelta, timezone

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import (
    get_user_role,
    set_premium_until,
    ensure_user_exists,
)

# =============================
# FSM KEY
# =============================

MANAGER_AWAIT_PREMIUM = "manager_await_premium"

# =============================
# KEYBOARD
# =============================

MANAGER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["⭐ Активировать Premium"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)

def _normalize(text: str) -> str:
    """
    Telegram/телефоны иногда отправляют разные варианты эмодзи (⭐ vs ⭐️),
    визуально одинаково, но строка другая -> if не срабатывает.
    """
    return (
        text.replace("⭐️", "⭐")
            .replace("⬅", "⬅️")   # на всякий случай (редко, но бывает)
            .strip()
    )

# =============================
# START (импортируется в start.py)
# =============================

async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message:
        return

    ensure_user_exists(user.id, user.username or "")
    context.user_data.clear()

    await update.message.reply_text(
        "🧑‍💼 Панель менеджера",
        reply_markup=MANAGER_KEYBOARD,
    )

# =============================
# TEXT ROUTER (ТОЛЬКО MANAGER / OWNER)
# =============================

async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if not user or not message or not message.text:
        return

    ensure_user_exists(user.id, user.username or "")

    role = get_user_role(user.id)
    if role not in ("manager", "owner"):
        return  # не менеджер — пропускаем

    text = _normalize(message.text)

    # EXIT
    if text == "⬅️ Выйти":
        context.user_data.clear()
        await manager_start(update, context)
        return

    # START PREMIUM FLOW
    # (ловим оба варианта: "⭐ ..." и "⭐️ ..." через normalize)
    if text.startswith("⭐") and "Активировать Premium" in text:
        context.user_data.clear()
        context.user_data[MANAGER_AWAIT_PREMIUM] = True

        await message.reply_text(
            "⭐ Активация Premium\n\n"
            "Отправь сообщение в формате:\n"
            "TELEGRAM_ID ДНИ\n\n"
            "Пример:\n"
            "123456789 30"
        )
        return

    # HANDLE PREMIUM INPUT
    if context.user_data.get(MANAGER_AWAIT_PREMIUM):
        parts = text.split()
        if len(parts) != 2:
            await message.reply_text("❌ Формат: TELEGRAM_ID ДНИ")
            return

        tg_id, days = parts
        if not tg_id.isdigit() or not days.isdigit():
            await message.reply_text("❌ ID и дни должны быть числами")
            return

        tg_id = int(tg_id)
        days = int(days)

        if days <= 0:
            await message.reply_text("❌ Количество дней должно быть больше 0")
            return

        ensure_user_exists(tg_id, "")

        premium_until = datetime.now(timezone.utc) + timedelta(days=days)
        set_premium_until(tg_id, premium_until)

        context.user_data.clear()

        await message.reply_text(
            "✅ Premium активирован\n\n"
            f"👤 Пользователь: {tg_id}\n"
            f"⏳ Срок: {days} дней",
            reply_markup=MANAGER_KEYBOARD,
        )

        try:
            await context.bot.send_message(
                chat_id=tg_id,
                text=(
                    "🎉 Вам активирован Premium!\n\n"
                    f"⏳ Срок действия: {days} дней"
                ),
            )
        except Exception:
            pass

        return

    # ВАЖНО: чтобы менеджер не думал, что “кнопка не работает”
    await message.reply_text(
        "ℹ️ Команда не распознана.\n"
        "Используй кнопки панели менеджера.",
        reply_markup=MANAGER_KEYBOARD,
    )

# =============================
# REGISTER
# =============================

def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router, block=False),
        group=1,
    )
