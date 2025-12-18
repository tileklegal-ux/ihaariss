# handlers/role_actions.py
from telegram import Update
from telegram.ext import ContextTypes

from database.db import ensure_user_exists, set_user_role, get_user_role


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE, manager_id: int | None = None):
    if manager_id is None:
        text = (update.message.text or "").strip()
        if not text.isdigit():
            await update.message.reply_text("Пришли Telegram ID числом.")
            return
        manager_id = int(text)

    ensure_user_exists(manager_id, "")

    set_user_role(manager_id, "manager")

    await update.message.reply_text(
        f"✅ Менеджер назначен.\nTelegram ID: {manager_id}"
    )


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE, manager_id: int | None = None):
    if manager_id is None:
        text = (update.message.text or "").strip()
        if not text.isdigit():
            await update.message.reply_text("Пришли Telegram ID числом.")
            return
        manager_id = int(text)

    role = get_user_role(manager_id)
    if role != "manager":
        await update.message.reply_text(
            f"ℹ️ У пользователя нет роли менеджера.\nTelegram ID: {manager_id}"
        )
        return

    set_user_role(manager_id, "user")

    await update.message.reply_text(
        f"✅ Менеджер удалён.\nTelegram ID: {manager_id}"
    )
