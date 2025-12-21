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

# =============================
# START (ИМЕННО ЭТУ ФУНКЦИЮ ИМПОРТИРУЕТ start.py)
# =============================

async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    ensure_user_exists(user.id)
    context.user_data.clear()

    await update.message.reply_text(
        "🧑‍💼 Панель менеджера",
        reply_markup=MANAGER_KEYBOARD,
    )

# =============================
# TEXT ROUTER (ТОЛЬКО ДЛЯ MANAGER / OWNER)
# =============================

async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message:
        return

    user_id = user.id
    ensure_user_exists(user_id)

    role = get_user_role(user_id)
    if role not in ("manager", "owner"):
        return  # ⛔ НЕ МЕНЕДЖЕР — НЕ НАШ ПАЦИЕНТ

    text = update.message.text.strip()

    # -------------------------
    # EXIT
    # -------------------------
    if text == "⬅️ Выйти":
        context.user_data.clear()
        await manager_start(update, context)
        return

    # -------------------------
    # START PREMIUM FLOW
    # -------------------------
    if text == "⭐ Активировать Premium":
        context.user_data[MANAGER_AWAIT_PREMIUM] = True
        await update.message.reply_text(
            "⭐ Активация Premium\n\n"
            "Отправь:\n"
            "TELEGRAM_ID ДНИ\n\n"
            "Пример:\n"
            "123456789 30"
        )
        return

    # -------------------------
    # HANDLE PREMIUM INPUT
    # -------------------------
    if context.user_data.get(MANAGER_AWAIT_PREMIUM):
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("❌ Формат: TELEGRAM_ID ДНИ")
            return

        tg_id, days = parts
        if not tg_id.isdigit() or not days.isdigit():
            await update.message.reply_text("❌ ID и дни должны быть числами")
            return

        tg_id = int(tg_id)
        days = int(days)
        if days <= 0:
            await update.message.reply_text("❌ Дни > 0")
            return

        ensure_user_exists(tg_id)

        premium_until = datetime.now(timezone.utc) + timedelta(days=days)
        set_premium_until(tg_id, premium_until)

        context.user_data.clear()

        await update.message.reply_text(
            f"✅ Premium активирован\n\n"
            f"👤 {tg_id}\n"
            f"⏳ {days} дней",
            reply_markup=MANAGER_KEYBOARD,
        )

        try:
            await context.bot.send_message(
                chat_id=tg_id,
                text=(
                    "🎉 Вам активирован Premium\n\n"
                    f"⏳ Срок: {days} дней"
                ),
            )
        except Exception:
            pass

        return

# =============================
# REGISTER (ДОЛЖЕН БЫТЬ РАНЬШЕ user handler)
# =============================

def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=1,  # 👈 раньше user (у тебя user = group=4)
    )
