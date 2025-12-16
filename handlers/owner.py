from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters, Application
from database.db import get_user_role

OWNER_KB = ReplyKeyboardMarkup(
    [
        [KeyboardButton("➕ Добавить менеджера")],
        [KeyboardButton("➖ Удалить менеджера")],
        [KeyboardButton("📊 Статистика")],
    ],
    resize_keyboard=True,
)

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "owner":
        return

    await update.message.reply_text(
        "👑 Панель владельца\n\n"
        "Управление системой:",
        reply_markup=OWNER_KB,
    )

async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "owner":
        return

    text = update.message.text

    if text == "➕ Добавить менеджера":
        await update.message.reply_text("Функция добавления менеджера")
        return

    if text == "➖ Удалить менеджера":
        await update.message.reply_text("Функция удаления менеджера")
        return

    if text == "📊 Статистика":
        await update.message.reply_text("Статистика проекта")
        return


def register_owner_handlers(app: Application):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, owner_text_router),
        group=1,
    )
