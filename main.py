import logging
import warnings

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from database.db import init_db, create_or_update_user, get_user_role

# USER
from handlers.user import (
    cmd_start_user,
    register_handlers_user,
)

# OWNER
from handlers.owner import (
    owner_panel,
    register_owner_handlers,
)

# MANAGER
from handlers.manager import (
    register_manager_handlers,
)

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ==================================================
# MIDDLEWARE
# ==================================================
async def save_user_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        u = update.effective_user
        create_or_update_user(
            telegram_id=u.id,
            username=u.username or "",
            first_name=u.first_name or "",
        )


# ==================================================
# /start — КАНОНИЧЕСКИЙ РОУТЕР
# ==================================================
async def cmd_start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)

    if role == "owner":
        await owner_panel(update, context)
        return

    if role == "manager":
        await update.message.reply_text(
            "🧑‍💼 Режим менеджера\n\n"
            "Используй доступные команды."
        )
        return

    await cmd_start_user(update, context)


# ==================================================
# MAIN
# ==================================================
def main():
    init_db()

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, save_user_middleware),
        group=-1,
    )

    application.add_handler(
        CommandHandler("start", cmd_start_router),
        group=0,
    )

    register_owner_handlers(application)
    register_manager_handlers(application)
    register_handlers_user(application)

    application.run_polling()


if __name__ == "__main__":
    main()
