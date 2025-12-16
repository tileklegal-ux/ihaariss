# main.py
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
    manager_panel,
    register_manager_handlers,
)

# OWNER
from handlers.owner import (
    owner_panel,
    register_owner_handlers,
)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ==================================================
# /start — ЕДИНАЯ ТОЧКА ВХОДА
# ==================================================
async def cmd_start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        role = get_user_role(user_id)
    except Exception:
        logger.exception("get_user_role failed in /start router, fallback to user")
        role = "user"

    if role == "owner":
        await owner_panel(update, context)
        return

    if role == "manager":
        await manager_panel(update, context)
        return

    await cmd_start_user(update, context)


# ==================================================
# MAIN
# ==================================================
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start — ВСЕГДА ПЕРВЫМ
    application.add_handler(
        CommandHandler("start", cmd_start_router),
        group=0,
    )

    # OWNER text handlers (group 1)
    register_owner_handlers(application)

    # MANAGER handlers (groups 1..3)
    register_manager_handlers(application)

    # USER text router (group 4)
    register_handlers_user(application)

    application.run_polling()


if __name__ == "__main__":
    main()
