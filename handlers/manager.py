# handlers/manager.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, Application

from database.db import set_premium_until
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
    text = update.message.text

    if text == "⭐ Выдать Premium":
        context.user_data["awaiting_premium_username"] = True
        await update.message.reply_text("Отправь @username пользователя")
        return

    if context.user_data.get("awaiting_premium_username"):
        username = text.lstrip("@")
        # 30 дней
        premium_until = int(time.time()) + 30 * 24 * 60 * 60
        from database.db import get_user_by_username

        user = get_user_by_username(username)
        if not user:
            await update.message.reply_text("Пользователь не найден")
            return

        set_premium_until(user[0], premium_until)
        context.user_data.clear()
        await update.message.reply_text("✅ Premium активирован")
        return

    if text == "⬅️ Выйти":
        await manager_start(update, context)
        return


def register_manager_handlers(app: Application):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=2,
    )
