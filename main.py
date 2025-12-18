# main.py

from telegram.ext import Application

from config import BOT_TOKEN
from database.db import init_db

from handlers.start import register_start_handlers
from handlers.owner import register_owner_handlers
from handlers.manager import register_manager_handlers
from handlers.user import register_user_handlers
from handlers.role_actions import role_actions_router
from telegram.ext import MessageHandler, filters


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    register_start_handlers(app)
    register_owner_handlers(app)
    register_manager_handlers(app)
    register_user_handlers(app)

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, role_actions_router),
        group=3,
    )

    app.run_polling()


if __name__ == "__main__":
    main()
