# handlers/owner.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, Application, CommandHandler

from handlers.role_actions import add_manager, remove_manager

OWNER_MENU = ReplyKeyboardMarkup(
    [
        ["📊 Статистика"],
        ["➕ Назначить менеджера", "➖ Убрать менеджера"],
        ["🏠 В меню"],
    ],
    resize_keyboard=True,
)


async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 Панель владельца.\n\n"
        "Команды:\n"
        "/add_manager <id или @username>\n"
        "/remove_manager <id или @username>\n",
        reply_markup=OWNER_MENU,
    )


async def owner_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "➕ Назначить менеджера":
        await update.message.reply_text("Формат: /add_manager <telegram_id или @username>")
        return

    if text == "➖ Убрать менеджера":
        await update.message.reply_text("Формат: /remove_manager <telegram_id или @username>")
        return

    if text == "📊 Статистика":
        # Если у тебя есть handlers/owner_stats.py — подключишь тут.
        await update.message.reply_text("Статистика подключится через handlers/owner_stats.py")
        return

    if text == "🏠 В меню":
        await owner_start(update, context)
        return


def register_handlers_owner(app: Application):
    # /owner на всякий случай
    app.add_handler(CommandHandler("owner", owner_start))

    # commands role_actions
    app.add_handler(CommandHandler("add_manager", add_manager))
    app.add_handler(CommandHandler("remove_manager", remove_manager))

    # кнопки владельца
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, owner_menu_click))
