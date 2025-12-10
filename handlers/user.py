from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from services.artbazar_table_flow import (
    start_artbazar_table,
    process_artbazar_answer,
    SESSION_KEY,
)


async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Тестовая команда из архитектурного скелета.
    Можно оставить как есть.
    """
    await update.message.reply_text("USER панель (каркас)")


async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /analysis — запускает Artbazar AI Таблицу.
    """
    await start_artbazar_table(update, context)


async def user_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Любое текстовое сообщение пользователя попадает сюда.
    Если сейчас идёт заполнение таблицы — передаём ответ в флоу.
    Если нет — игнорируем или выводим подсказку.
    """

    # Проверяем, начат ли процесс заполнения таблицы
    if SESSION_KEY in context.user_data:
        # Пользователь в процессе — отправляем текст в обработчик
        await process_artbazar_answer(update, context)
        return

    # Если пользователь пишет какие-то тексты вне флоу таблицы:
    await update.message.reply_text(
        "Я тебя слышу, но ты не запустил Artbazar AI Таблицу.\n"
        "Напиши /analysis, чтобы начать расчёт."
    )


def register_user_handlers(app):
    """
    Регистрируем все необходимые user-хендлеры.
    Вызывается из main.py.
    """

    # /user — тестовая команда
    app.add_handler(CommandHandler("user", user_command))

    # /analysis — запуск таблицы
    app.add_handler(CommandHandler("analysis", analysis_command))

    # Все текстовые сообщения → роутер user_message_router
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message_router))
