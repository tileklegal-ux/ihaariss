from telegram.ext import Application

from config import BOT_TOKEN
from handlers.start import register_start_handlers

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # /start (роутер по ролям)
    register_start_handlers(application)

    # ❗ ВАЖНО:
    # user.py НЕ регистрируется тут как отдельный модуль
    # Все text handlers живут внутри user.text_router()

    application.run_polling()


if __name__ == "__main__":
    main()
