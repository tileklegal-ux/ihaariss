from telegram.ext import Application

from config import BOT_TOKEN
from database.db import init_db

from handlers.start import register_start_handlers
from handlers.user import register_user_handlers
from handlers.owner import register_handlers_owner


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # /start + init user
    register_start_handlers(app)

    # user FSM / premium / ai
    register_user_handlers(app)

    # owner / manager
    register_handlers_owner(app)

    app.run_polling()


if __name__ == "__main__":
    main()
