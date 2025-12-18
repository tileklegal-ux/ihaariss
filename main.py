from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from handlers.start import register_start_handlers

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    register_start_handlers(app)
    app.run_polling()

if __name__ == "__main__":
    main()
