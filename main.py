# main.py
import logging
from telegram.ext import Application

from handlers.user import register_handlers_user
from handlers.owner import register_handlers_owner
from handlers.manager import register_handlers_manager

from config import TELEGRAM_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Порядок ВАЖЕН
    # owner / manager идут раньше user
    register_handlers_owner(app)    # group 1
    register_handlers_manager(app)  # group 2
    register_handlers_user(app)     # group 4

    app.run_polling()

if __name__ == "__main__":
    main()
