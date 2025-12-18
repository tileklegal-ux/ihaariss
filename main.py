import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_TOKEN
from database.db import get_user_role, ensure_user_exists

from handlers.user import cmd_start_user, register_handlers_user
from handlers.owner import owner_start, register_handlers_owner
from handlers.manager import manager_start, register_handlers_manager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username

    ensure_user_exists(user_id, username)

    role = get_user_role(user_id)

    if role == "owner":
        await owner_start(update, context)
        return

    if role == "manager":
        await manager_start(update, context)
        return

    await cmd_start_user(update, context)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # ✅ ЕДИНСТВЕННЫЙ /start
    app.add_handler(CommandHandler("start", start_router), group=0)

    # ✅ порядок важен
    register_handlers_owner(app)      # group 2
    register_handlers_manager(app)    # group 3
    register_handlers_user(app)       # group 4

    app.run_polling()


if __name__ == "__main__":
    main()
