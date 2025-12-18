from telegram import Update
from telegram.ext import ContextTypes

from database.db import set_user_role, get_user_by_username


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("Пользователь не найден")
        return

    user_id = user[0]
    set_user_role(user_id, "manager")

    await update.message.reply_text(f"Менеджер @{username} добавлен")


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("Пользователь не найден")
        return

    user_id = user[0]
    set_user_role(user_id, "user")

    await update.message.reply_text(f"Менеджер @{username} удалён")
