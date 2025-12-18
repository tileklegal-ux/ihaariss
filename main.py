# main.py
import os

from telegram.ext import Application

from database.db import init_db
from handlers.start import register_start_handlers
from handlers.owner import register_owner_handlers
from handlers.manager import register_manager_handlers
from handlers.user import register_handlers_user


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    init_db()

    app = Application.builder().token(token).build()

    register_start_handlers(app)
    register_owner_handlers(app)
    register_manager_handlers(app)
    register_handlers_user(app)

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
