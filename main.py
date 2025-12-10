import logging
from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN
from handlers.owner import owner_command
from handlers.manager import manager_command
from handlers.user import user_command, analysis_start

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update, context):
    await update.message.reply_text("Artbazar AI бот запущен")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Базовые команды
    app.add_handler(CommandHandler("start", start))

    # Роли
    app.add_handler(CommandHandler("owner", owner_command))
    app.add_handler(CommandHandler("manager", manager_command))
    app.add_handler(CommandHandler("user", user_command))

    # Artbazar AI Таблица — две команды
    app.add_handler(CommandHandler("analysis", analysis_start))   # Основная
    app.add_handler(CommandHandler("analyze", analysis_start))    # Алиас

    app.run_polling()

if __name__ == "__main__":
    main()
