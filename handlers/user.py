from telegram import Update
from telegram.ext import ContextTypes
from services.artbazar_table_flow import start_table_flow

# Временная заглушка для /user
async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команда USER: здесь будет пользовательское меню."
    )

# Главная функция запуска Artbazar AI Таблицы
async def analysis_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_table_flow(update, context)
