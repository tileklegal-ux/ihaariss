# handlers/owner.py
# -*- coding: utf-8 -*-
import logging

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
    Application,
)

from database.db import get_user_role

logger = logging.getLogger(__name__)

# =========================
# OWNER KEYBOARD
# =========================
BTN_OWNER_ADD_MANAGER = "➕ Добавить менеджера"
BTN_OWNER_DEL_MANAGER = "➖ Удалить менеджера"
BTN_OWNER_STATS = "📊 Статистика"
BTN_OWNER_EXIT = "⬅️ Выйти в главное меню"


def owner_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_OWNER_ADD_MANAGER), KeyboardButton(BTN_OWNER_DEL_MANAGER)],
            [KeyboardButton(BTN_OWNER_STATS)],
            [KeyboardButton(BTN_OWNER_EXIT)],
        ],
        resize_keyboard=True,
    )


# =========================
# OWNER ENTRY POINT (вызывается из main.py /start router)
# =========================
async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        role = get_user_role(update.effective_user.id)
    except Exception:
        logger.exception("get_user_role failed in owner_panel")
        return

    if role != "owner":
        return

    context.user_data.clear()

    await update.message.reply_text(
        "👑 Панель владельца\n\n"
        "Тут управляется система.\n"
        "• менеджеры\n"
        "• статистика\n\n"
        "Выбери действие 👇",
        reply_markup=owner_keyboard(),
    )


# =========================
# OWNER TEXT ROUTER
# =========================
async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        role = get_user_role(update.effective_user.id)
    except Exception:
        logger.exception("get_user_role failed in owner_text_router")
        return

    if role != "owner":
        return

    text = (update.message.text or "").strip()

    if text == BTN_OWNER_ADD_MANAGER:
        await update.message.reply_text(
            "➕ Добавить менеджера\n\n"
            "Заготовка. Тут будет назначение менеджера.\n"
            "Сейчас логика назначения/снятия — в разработке.",
            reply_markup=owner_keyboard(),
        )
        return

    if text == BTN_OWNER_DEL_MANAGER:
        await update.message.reply_text(
            "➖ Удалить менеджера\n\n"
            "Заготовка. Тут будет снятие менеджера.\n"
            "Сейчас логика назначения/снятия — в разработке.",
            reply_markup=owner_keyboard(),
        )
        return

    if text == BTN_OWNER_STATS:
        await update.message.reply_text(
            "📊 Статистика\n\n"
            "Заготовка. Тут будет статистика по продукту.\n"
            "(пользователи, premium, активность, конверсия).",
            reply_markup=owner_keyboard(),
        )
        return

    if text == BTN_OWNER_EXIT:
        # Возврат в общий /start (единая точка входа)
        await update.message.reply_text(
            "Ок. Возвращаю в главное меню. Нажми /start",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/start")]], resize_keyboard=True),
        )
        return


# =========================
# REGISTER
# =========================
def register_owner_handlers(app: Application):
    """
    ВАЖНО:
    - НЕ регистрируем /start здесь.
    - /start обрабатывается ТОЛЬКО в main.py (cmd_start_router).
    - Тут только текстовые кнопки владельца.
    """
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, owner_text_router),
        group=1,
    )
