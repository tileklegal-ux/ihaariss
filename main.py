import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from database.db import get_user_role

# USER
from handlers.user import (
    cmd_start_user,
    register_handlers_user,
)

# MANAGER
from handlers.manager import (
    register_manager_handlers,
)

# OWNER
from handlers.owner import register_handlers_owner

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ==================================================
# /start — ROUTER ТОЛЬКО ДЛЯ USER
# ==================================================
async def cmd_start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        role = get_user_role(user_id)
    except Exception:
        role = "user"

    # OWNER и MANAGER сюда не заходят
    if role in ("owner", "manager"):
        return

    await cmd_start_user(update, context)


# ==================================================
# MAIN
# ==================================================
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # OWNER — САМЫЙ ПЕРВЫЙ
    register_handlers_owner(application)

    # MANAGER
    register_manager_handlers(application)

    # USER /start
    application.add_handler(
        CommandHandler("start", cmd_start_router),
        group=3,
    )

    # USER остальной текст
    register_handlers_user(application)

    application.run_polling()


if __name__ == "__main__":
    main()
