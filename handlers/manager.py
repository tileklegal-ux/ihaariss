# handlers/manager.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import get_user_role

MANAGER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["⭐ Активировать Premium"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)


async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧑‍💼 Панель менеджера",
        reply_markup=MANAGER_KEYBOARD,
    )


async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if get_user_role(user_id) != "manager":
        return

    text = (update.message.text or "").strip()

    if text == "⭐ Активировать Premium":
        await update.message.reply_text(
            "Отправь Telegram ID пользователя, которому нужно активировать Premium (числом).\n\n"
            "Как узнать Telegram ID:\n"
            "1️⃣ Напиши боту @userinfobot\n"
            "2️⃣ Скопируй ID\n"
            "3️⃣ Пришли сюда числом"
        )
        return

    if text == "⬅️ Выйти":
        await update.message.reply_text("Выход из панели менеджера")
        return


def register_manager_handlers(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router), group=1)
