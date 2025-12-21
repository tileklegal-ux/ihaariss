# handlers/manager.py

from datetime import datetime, timedelta, timezone

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
    ApplicationHandlerStop,
)

from database.db import (
    get_user_role,
    set_premium_until,
    ensure_user_exists,
)

# =============================
# FSM KEY (ТОЛЬКО ДЛЯ МЕНЕДЖЕРА)
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
# START
# (ЭТУ ФУНКЦИЮ ИМПОРТИРУЕТ start.py)
# =============================

async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message:
        return ApplicationHandlerStop

    ensure_user_exists(user.id)
    context.user_data.clear()

    await update.message.reply_text(
        "🧑‍💼 Панель менеджера",
        reply_markup=MANAGER_KEYBOARD,
    )

    return ApplicationHandlerStop


# =============================
# TEXT ROUTER
# (ТОЛЬКО ДЛЯ manager / owner)
# =============================

async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if not user or not message or not message.text:
        return

    user_id = user.id
    ensure_user_exists(user_id)

    role = get_user_role(user_id)
    if role not in ("manager", "owner"):
        return  # ⛔ не менеджер — пропускаем дальше

    text = message.text.strip()

    # -------------------------
    # EXIT
    # -------------------------
    if text == "⬅️ Выйти":
        context.user_data.clear()
        await manager_start(update, context)
        return ApplicationHandlerStop

    # -------------------------
    # START PREMIUM FLOW
    # -------------------------
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
        return ApplicationHandlerStop

    # -------------------------
    # HANDLE PREMIUM INPUT
    # -------------------------
    if context.user_data.get(MANAGER_AWAIT_PREMIUM):
        parts = text.split()
        if len(parts) != 2:
            await message.reply_text("❌ Формат: TELEGRAM_ID ДНИ")
            return ApplicationHandlerStop

        tg_id, days = parts

        if not tg_id.isdigit() or not days.isdigit():
            await message.reply_text("❌ ID и дни должны быть числами")
            return ApplicationHandlerStop

        tg_id = int(tg_id)
        days = int(days)

        if days <= 0:
            await message.reply_text("❌ Количество дней должно быть больше 0")
            return ApplicationHandlerStop

        ensure_user_exists(tg_id)

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
                    f"⏳ Срок действия: {days} дней\n\n"
                    "Теперь доступны расширенные функции 🚀"
                ),
            )
        except Exception:
            pass

        return ApplicationHandlerStop

    # Любое другое сообщение менеджера — не пускать в user.py
    return ApplicationHandlerStop


# =============================
# REGISTER
# (ВАЖНО: РАНЬШЕ user handler)
# =============================

def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            manager_text_router,
            block=True,   # 🔒 жёстко блокируем цепочку
        ),
        group=1,        # 👈 ДО user (user у тебя = group=4)
    )
