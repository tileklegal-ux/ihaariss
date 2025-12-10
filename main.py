from dotenv import load_dotenv
load_dotenv()

import logging
from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from database.db import init_db  # ← добавили
from handlers.owner import owner_command
from handlers.manager import give_premium, extend_premium, remove_premium_cmd
from handlers.user import register_user_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def start(update, context):
    await update.message.reply_text("Artbazar AI бот запущен")


def main():
    # 🔥 ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ (Railway создаст таблицы)
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # Базовая команда
    app.add_handler(CommandHandler("start", start))

    # Owner
    app.add_handler(CommandHandler("owner", owner_command))

    # Manager commands (работают по username)
    app.add_handler(CommandHandler("give_premium", give_premium))
    app.add_handler(CommandHandler("extend_premium", extend_premium))
    app.add_handler(CommandHandler("remove_premium", remove_premium_cmd))

    # User handlers (analysis, etc.)
    register_user_handlers(app)

    # Запускаем polling
    app.run_polling()


if __name__ == "__main__":
    main()
