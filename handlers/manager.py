from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters, Application
from database.db import get_user_role

MANAGER_KB = ReplyKeyboardMarkup(
    [[KeyboardButton("🟢 Активировать Premium")]],
    resize_keyboard=True,
)

async def manager_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "manager":
        return

    await update.message.reply_text(
        "🧑‍💼 Панель менеджера",
        reply_markup=MANAGER_KB,
    )

async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "manager":
        return

    if update.message.text == "🟢 Активировать Premium":
        await update.message.reply_text("Активация Premium (логика уже есть)")
        return


def register_manager_handlers(app: Application):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=2,
    )
