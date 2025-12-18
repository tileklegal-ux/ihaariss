# handlers/start_router.py

from telegram import Update
from telegram.ext import ContextTypes

from database.db import ensure_user_exists, get_user_role
from handlers.owner import owner_start
from handlers.manager import manager_start
from handlers.user import cmd_start_user


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user

    ensure_user_exists(
        user_id=u.id,
        username=u.username,
    )

    role = get_user_role(u.id)

    if role == "owner":
        await owner_start(update, context)
        return

    if role == "manager":
        await manager_start(update, context)
        return

    await cmd_start_user(update, context)
