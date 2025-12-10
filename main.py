from dotenv import load_dotenv
load_dotenv()

from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from handlers.owner import owner_command
from handlers.manager import manager_command
from handlers.user import register_user_handlers


async def start(update, context):
    await update.message.reply_text("Artbazar AI бот запущен")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Базовая команда
    app.add_handler(CommandHandler("start", start))

    # Команды owner и manager (каркас)
    app.add_handler(CommandHandler("owner", owner_command))
    app.add_handler(CommandHandler("manager", manager_command))

    # Регистрируем user-хендлеры (analysis, роутеры и т.д.)
    register_user_handlers(app)

    # Запуск polling
    app.run_polling()


if __name__ == "__main__":
    main()
