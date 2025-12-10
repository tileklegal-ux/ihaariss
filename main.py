from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN
from handlers.owner import owner_command
from handlers.manager import manager_command
from handlers.user import user_command

async def start(update, context):
    await update.message.reply_text("Artbazar AI бот запущен")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Базовая команда проверки
    app.add_handler(CommandHandler("start", start))

    # Каркас роутинга по ролям (пока тестовый)
    app.add_handler(CommandHandler("owner", owner_command))
    app.add_handler(CommandHandler("manager", manager_command))
    app.add_handler(CommandHandler("user", user_command))

    app.run_polling()

if __name__ == "__main__":
    main()

