import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from database.db import ensure_user_exists, get_user_role
from handlers.owner import owner_start, register_handlers_owner
from handlers.user import user_text_router

TOKEN = "ТВОЙ_TOKEN"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    username = user.username

    ensure_user_exists(telegram_id, username)

    role = get_user_role(telegram_id)

    if telegram_id == 1974482384 or role == "owner":
        await owner_start(update, context)
        return

    await user_text_router(update, context)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_router), group=0)

    register_handlers_owner(app)

    app.run_polling()


if __name__ == "__main__":
    main()
