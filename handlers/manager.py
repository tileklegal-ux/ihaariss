from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import get_user_role, set_premium_until
import time


MANAGER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["💎 Активировать Premium"],
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

    # защита: только менеджер
    if get_user_role(user_id) != "manager":
        return

    text = update.message.text.strip()

    # ===== АКТИВАЦИЯ PREMIUM =====
    if text == "💎 Активировать Premium":
        context.user_data["await_premium_id"] = True
        await update.message.reply_text(
            "💎 Активация Premium\n\n"
            "Отправь Telegram ID пользователя, которому нужно активировать Premium.\n\n"
            "Как узнать Telegram ID:\n"
            "1️⃣ Напиши боту @userinfobot\n"
            "2️⃣ Скопируй ID\n"
            "3️⃣ Пришли сюда числом"
        )
        return

    # ===== ПОЛУЧЕН ID ПОЛЬЗОВАТЕЛЯ =====
    if context.user_data.get("await_premium_id"):
        try:
            target_id = int(text)
        except ValueError:
            await update.message.reply_text("❌ Telegram ID должен быть числом")
            return

        # Premium на 30 дней
        premium_until = int(time.time()) + 30 * 24 * 60 * 60
        set_premium_until(target_id, premium_until)

        context.user_data.pop("await_premium_id", None)

        await update.message.reply_text(
            f"✅ Premium активирован\n\n"
            f"Telegram ID: {target_id}\n"
            f"Срок: 30 дней"
        )
        return

    # ===== ВЫХОД =====
    if text == "⬅️ Выйти":
        context.user_data.clear()
        await update.message.reply_text("⬅️ Выход из панели менеджера")
        return


def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=1,
    )
