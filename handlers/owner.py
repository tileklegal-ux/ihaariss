# handlers/owner.py
# -*- coding: utf-8 -*-

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters, ApplicationHandlerStop

from database.db import get_user_role

logger = logging.getLogger(__name__)

BTN_OWNER_PANEL = "👑 Панель владельца"
BTN_OWNER_EXIT = "⬅️ Выйти в главное меню"

def owner_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_OWNER_EXIT)],
        ],
        resize_keyboard=True,
    )

async def owner_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Вход в панель владельца.
    """
    text = (
        "👑 Панель владельца\n\n"
        "Здесь будут админ-функции.\n"
        "Пока что: выход обратно в главное меню."
    )
    await update.message.reply_text(text, reply_markup=owner_keyboard())

async def owner_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выход из панели владельца — просто возвращаем пользователя в обычное меню.
    Само меню рисуется в user.py (главное меню).
    """
    await update.message.reply_text("Выход из панели владельца")

async def owner_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Перехватываем только owner-события.
    ВАЖНО: если это owner и кнопка наша — останавливаем дальнейшую обработку,
    чтобы user.py не дал дубль/конфликт.
    """
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        return

    text = (update.message.text or "").strip()

    if text == BTN_OWNER_PANEL:
        await owner_entry(update, context)
        raise ApplicationHandlerStop

    if text == BTN_OWNER_EXIT:
        await owner_exit(update, context)
        raise ApplicationHandlerStop

    # Всё остальное owner пусть обрабатывает user.py как обычный пользователь
    return

def register_owner_handlers(app):
    # Один общий роутер на owner-кнопки
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, owner_router),
        group=1,
    )
