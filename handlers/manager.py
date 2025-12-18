from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import get_user_role, set_premium_until
import time


MANAGER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["⭐ Выдать Premium"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)


async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧑‍💼 Панель менеджера",
        reply_markup=MANAGER_KEYBOARD,
    )


async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if get_user_role(user_id) != "manager":
        return

    text = update.message.text

    if text == "⭐ Выдать Premium":
        context.user_data["await_premium_user"] = True
        await update.message.reply_text("Введи username пользователя (@username)")
        return

    if text == "⬅️ Выйти":
        await update.message.reply_text("Выход из панели менеджера")
        return

    if context.user_data.get("await_premium_user"):
        username = text.lstrip("@")
        from database.db import get_user_by_username

        user = get_user_by_username(username)
        if not user:
            await update.message.reply_text("Пользователь не найден")
            return

        target_user_id = user[0]
        premium_until = int(time.time()) + 30 * 24 * 60 * 60  # 30 дней
        set_premium_until(target_user_id, premium_until)

        context.user_data["await_premium_user"] = False
        await update.message.reply_text(f"Premium выдан пользователю @{username}")


def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=2,
    )
