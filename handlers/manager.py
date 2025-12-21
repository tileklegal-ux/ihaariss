# handlers/manager.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import ensure_user_exists, get_user_role, set_premium_until

# =============================
# FSM KEY (только для manager)
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
# START (вызывается из start_router.py)
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
# TEXT ROUTER (ТОЛЬКО manager/owner)
# =============================
async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    if not user or not message or not message.text:
        return

    ensure_user_exists(user.id, user.username or "")

    role = get_user_role(user.id)
    if role not in ("manager", "owner"):
        return

    text = message.text.strip()

    # Выход
    if text == "⬅️ Выйти":
        context.user_data.clear()
        await manager_start(update, context)
        return

    # Старт активации Premium
    if text == "⭐ Активировать Premium":
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

    # Обработка ввода TELEGRAM_ID ДНИ
    if context.user_data.get(MANAGER_AWAIT_PREMIUM):
        parts = text.split()
        if len(parts) != 2:
            await message.reply_text("❌ Формат: TELEGRAM_ID ДНИ")
            return

        tg_id_s, days_s = parts
        if not tg_id_s.isdigit() or not days_s.isdigit():
            await message.reply_text("❌ ID и дни должны быть числами")
            return

        tg_id = int(tg_id_s)
        days = int(days_s)
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

        # уведомление пользователю — не критично, если не дойдёт
        try:
            await context.bot.send_message(
                chat_id=tg_id,
                text="🎉 Вам активирован Premium!\n\n" f"⏳ Срок: {days} дней",
            )
        except Exception:
            pass

        return


# =============================
# REGISTER
# ВАЖНО: фильтр узкий, чтобы manager не перехватывал owner/user
# =============================
def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^(⭐ Активировать Premium|⬅️ Выйти|\d+\s+\d+)$"),
            manager_text_router,
        ),
        group=2,
    )
