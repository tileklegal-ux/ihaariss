from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from database.db import get_user_role, ensure_user_exists
from handlers.owner import owner_start
from handlers.manager import manager_start
from handlers.user import user_start


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # гарантируем пользователя в БД
    ensure_user_exists(
        user.id,
        user.username,
    )

    role = get_user_role(user.id)

    if role == "owner":
        await owner_start(update, context)
        return

    if role == "manager":
        await manager_start(update, context)
        return

    await user_start(update, context)


def register_start_handlers(app):
    app.add_handler(CommandHandler("start", start_router), group=0)
