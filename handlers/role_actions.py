# handlers/role_actions.py
# Управление ролями и Premium (FSM через context.user_data)

from __future__ import annotations

from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, Application

from database.db import (
    get_user_role,
    get_user_by_username,
    set_role_by_telegram_id,
    give_premium_days,
)

# -----------------------------
# BUTTONS (используются в owner/manager)
# -----------------------------
BTN_GIVE_PREMIUM = "✅ Выдать Premium"
BTN_EXIT = "⬅️ Выйти"


# -----------------------------
# OWNER: управление менеджерами
# -----------------------------
async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос username менеджера у владельца"""
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        return

    await update.message.reply_text(
        "Введите username менеджера (без @):\nПример: username123"
    )
    context.user_data["awaiting_manager_add"] = True
    context.user_data.pop("awaiting_manager_remove", None)


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос username менеджера для удаления у владельца"""
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        return

    await update.message.reply_text(
        "Введите username менеджера для удаления (без @):\nПример: username123"
    )
    context.user_data["awaiting_manager_remove"] = True
    context.user_data.pop("awaiting_manager_add", None)


async def _apply_manager_role_by_username(update: Update, username: str, new_role: str) -> bool:
    """Меняет роль пользователю по username. Возвращает True если найден и изменён."""
    username = username.lstrip("@").strip()
    if not username:
        return False

    user = get_user_by_username(username)
    if not user:
        await update.message.reply_text(
            f"Пользователь @{username} не найден в базе.\n"
            "Важно: пользователь должен хотя бы раз нажать /start, чтобы попасть в БД."
        )
        return False

    set_role_by_telegram_id(user["telegram_id"], new_role)
    return True


async def handle_owner_manager_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстового ввода для owner FSM (добавить/удалить менеджера)."""
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        return

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if context.user_data.get("awaiting_manager_add"):
        context.user_data.pop("awaiting_manager_add", None)
        ok = await _apply_manager_role_by_username(update, text, "manager")
        if ok:
            await update.message.reply_text(
                f"Менеджер @{text.lstrip('@').strip()} добавлен. Роль изменена на 'manager'."
            )
        return

    if context.user_data.get("awaiting_manager_remove"):
        context.user_data.pop("awaiting_manager_remove", None)
        ok = await _apply_manager_role_by_username(update, text, "user")
        if ok:
            await update.message.reply_text(
                f"Менеджер @{text.lstrip('@').strip()} удалён. Роль изменена на 'user'."
            )
        return


# -----------------------------
# MANAGER: выдача Premium
# -----------------------------
async def give_premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Старт FSM для выдачи Premium (менеджер)."""
    role = get_user_role(update.effective_user.id)
    if role != "manager":
        return

    await update.message.reply_text(
        "Введите username пользователя (без @), которому выдать Premium:\nПример: client123"
    )
    context.user_data["awaiting_premium_username"] = True
    context.user_data.pop("awaiting_premium_days", None)
    context.user_data.pop("premium_target_telegram_id", None)


async def handle_manager_premium_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстового ввода для manager FSM (выдать Premium)."""
    role = get_user_role(update.effective_user.id)
    if role != "manager":
        return

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # Шаг 1: username
    if context.user_data.get("awaiting_premium_username"):
        context.user_data.pop("awaiting_premium_username", None)

        username = text.lstrip("@").strip()
        user = get_user_by_username(username)
        if not user:
            await update.message.reply_text(
                f"Пользователь @{username} не найден в базе.\n"
                "Важно: пользователь должен хотя бы раз нажать /start, чтобы попасть в БД."
            )
            return

        context.user_data["premium_target_telegram_id"] = user["telegram_id"]
        context.user_data["awaiting_premium_days"] = True

        await update.message.reply_text(
            "Введите количество дней Premium (целое число).\nПример: 30"
        )
        return

    # Шаг 2: days
    if context.user_data.get("awaiting_premium_days"):
        target_id = context.user_data.get("premium_target_telegram_id")
        context.user_data.pop("awaiting_premium_days", None)
        context.user_data.pop("premium_target_telegram_id", None)

        try:
            days = int(text)
            if days <= 0:
                raise ValueError("days must be positive")
        except Exception:
            await update.message.reply_text("Некорректно. Введите целое число дней, например: 30")
            return

        give_premium_days(int(target_id), days)
        until_mark = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        await update.message.reply_text(
            f"Premium выдан на {days} дней.\n"
            f"Техническая отметка: операция выполнена ({until_mark})."
        )
        return


# -----------------------------
# Регистрация FSM-хендлеров (group=1)
# -----------------------------
def register_role_actions(app: Application):
    """Group 1: FSM обработчики ввода для owner/manager (после /start роутера)."""
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, role_text_router),
        group=1,
    )


async def role_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Единый роутер FSM-ввода по ролям (owner/manager)."""
    role = get_user_role(update.effective_user.id)

    if role == "owner":
        await handle_owner_manager_input(update, context)
        return

    if role == "manager":
        await handle_manager_premium_input(update, context)
        return
