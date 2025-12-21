from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import get_user_role
from handlers.owner_stats import show_owner_stats
from handlers.role_actions import add_manager, remove_manager

OWNER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📊 Общая статистика"],
        ["➕ Добавить менеджера", "➖ Удалить менеджера"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)

OWNER_AWAIT_ACTION = "owner_await_action"     # "add" | "remove"
OWNER_AWAIT_ID = "owner_await_id"             # True


async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return

    context.user_data.clear()
    await update.message.reply_text("👑 Панель владельца", reply_markup=OWNER_KEYBOARD)


async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    if not user or not message or not message.text:
        return

    role = get_user_role(user.id)
    if role != "owner":
        return  # не owner — не трогаем, пусть дальше роутится

    text = message.text.strip()

    # Выйти
    if text == "⬅️ Выйти":
        context.user_data.clear()
        await owner_start(update, context)
        return

    # Статистика
    if text == "📊 Общая статистика":
        await show_owner_stats(update, context)
        return

    # Начать добавление менеджера
    if text == "➕ Добавить менеджера":
        context.user_data.clear()
        context.user_data[OWNER_AWAIT_ACTION] = "add"
        context.user_data[OWNER_AWAIT_ID] = True
        await message.reply_text("Отправь Telegram ID менеджера числом.")
        return

    # Начать удаление менеджера
    if text == "➖ Удалить менеджера":
        context.user_data.clear()
        context.user_data[OWNER_AWAIT_ACTION] = "remove"
        context.user_data[OWNER_AWAIT_ID] = True
        await message.reply_text("Отправь Telegram ID менеджера для удаления.")
        return

    # Принимаем ID после кнопок add/remove
    if context.user_data.get(OWNER_AWAIT_ID):
        if not text.isdigit():
            await message.reply_text("Пришли Telegram ID числом.")
            return

        target_id = int(text)
        action = context.user_data.get(OWNER_AWAIT_ACTION)

        if action == "add":
            await add_manager(update, context, target_id)
        elif action == "remove":
            await remove_manager(update, context, target_id)

        context.user_data.clear()
        return


def register_owner_handlers(app):
    # Важно: block=False, чтобы не мешать manager/user роутерам
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, owner_text_router, block=False),
        group=1,
    )
