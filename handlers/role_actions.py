# handlers/role_actions.py

from telegram import Update
from telegram.ext import ContextTypes

from database.db import set_user_role, get_user_by_username


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь @username менеджера")
    context.user_data["add_manager"] = True


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь @username менеджера для удаления")
    context.user_data["remove_manager"] = True


async def role_actions_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lstrip("@")

    if context.user_data.get("add_manager"):
        user = get_user_by_username(text)
        if not user:
            await update.message.reply_text("Пользователь не найден")
            return
        set_user_role(user[0], "manager")
        context.user_data.clear()
        await update.message.reply_text("✅ Менеджер добавлен")
        return

    if context.user_data.get("remove_manager"):
        user = get_user_by_username(text)
        if not user:
            await update.message.reply_text("Пользователь не найден")
            return
        set_user_role(user[0], "user")
        context.user_data.clear()
        await update.message.reply_text("❌ Менеджер удалён")
        return
