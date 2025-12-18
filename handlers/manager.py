from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import get_user_role, set_premium_until, ensure_user_exists
import time


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

    text = update.message.text.strip()

    # Кнопка Premium
    if text == "⭐ Активировать Premium":
        context.user_data["await_premium_id"] = True
        await update.message.reply_text(
            "⭐ *Активация Premium*\n\n"
            "Отправь *Telegram ID пользователя*, которому нужно активировать Premium.\n\n"
            "Как узнать Telegram ID:\n"
            "1️⃣ Напиши боту @userinfobot\n"
            "2️⃣ Скопируй ID\n"
            "3️⃣ Пришли сюда числом",
            parse_mode="Markdown",
        )
        return

    # Ввод Telegram ID
    if context.user_data.get("await_premium_id"):
        if not text.isdigit():
            await update.message.reply_text("❌ Нужно отправить Telegram ID числом.")
            return

        target_id = int(text)

        # гарантируем, что пользователь есть
        ensure_user_exists(target_id)

        # активируем Premium на 30 дней
        premium_until = int(time.time()) + 30 * 24 * 60 * 60
        set_premium_until(target_id, premium_until)

        context.user_data.pop("await_premium_id", None)

        await update.message.reply_text(
            f"✅ Premium активирован\nTelegram ID: {target_id}\n⏳ Срок: 30 дней"
        )
        return

    if text == "⬅️ Выйти":
        await update.message.reply_text("Выход из панели менеджера")
        return


def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=1,
    )
