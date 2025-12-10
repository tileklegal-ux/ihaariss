from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from services.artbazar_table_flow import (
    start_artbazar_table,
    process_artbazar_answer,
    SESSION_KEY,
)


async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Базовая команда /user — пока просто заглушка.
    """
    await update.message.reply_text("USER панель (каркас)")


async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /analysis и /analyze — запуск Artbazar AI Таблицы.
    """
    await start_artbazar_table(update, context)


async def user_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Роутер для всех текстовых сообщений.
    Если пользователь сейчас заполняет таблицу — отправляем ответы в флоу.
    Если нет — подсказываем, что делать.
    """
    # Если идёт сессия таблицы — шлём ответ в обработчик шагов
    if SESSION_KEY in context.user_data:
        await process_artbazar_answer(update, context)
        return

    # Если таблица не запущена
    await update.message.reply_text(
        "Я тебя слышу, но ты ещё не запустил Artbazar AI Таблицу.\n"
        "Напиши /analysis (или /analyze), чтобы начать расчёты."
    )


def register_user_handlers(app):
    """
    Регистрируем все user-хендлеры в Application.
    Вызывается из main.py.
    """

    # /user — базовая заглушка
    app.add_handler(CommandHandler("user", user_command))

    # /analysis — основная команда
    app.add_handler(CommandHandler("analysis", analysis_command))

    # /analyze — алиас той же команды
    app.add_handler(CommandHandler("analyze", analysis_command))

    # Все текстовые сообщения без команд — в роутер
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message_router))
