from telegram.ext import CommandHandler
from handlers.start_router import start_router

def register_start_handlers(app):
    app.add_handler(CommandHandler("start", start_router))
