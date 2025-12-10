from dotenv import load_dotenv
load_dotenv()

import logging
from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from handlers.owner import owner_command
from handlers.manager import manager_command
from handlers.user import register_user_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def start(update, context):
    await update.message.reply_text("Artbazar AI бот запущен")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Базовая команда
    app.add_handler(CommandHandler("start", start))

    # Команды для ролей (каркас)
    app.add_handler(CommandHandler("owner", owner_command))
    app.add_handler(CommandHandler("manager", manager_command))

    # Регистрируем все user-хендлеры (включая /analysis и /analyze)
    register_user_handlers(app)

    # Запускаем polling
    app.run_polling()


if __name__ == "__main__":
    main()
