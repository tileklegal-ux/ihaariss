from telegram import Update
from telegram.ext import ContextTypes

from database.db import (
    get_user_by_username,
    set_user_role,
)


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи username менеджера.")
        return

    username = context.args[0].lstrip("@")
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("Пользователь не найден.")
        return

    user_id = user[0]
    set_user_role(user_id, "manager")
    await update.message.reply_text(f"@{username} назначен менеджером.")


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи username менеджера.")
        return

    username = context.args[0].lstrip("@")
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("Пользователь не найден.")
        return

    user_id = user[0]
    set_user_role(user_id, "user")
    await update.message.reply_text(f"@{username} снят с роли менеджера.")
