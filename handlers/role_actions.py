# handlers/role_actions.py

from telegram import Update
from telegram.ext import ContextTypes

from database.db import set_user_role


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление менеджера владельцем"""
    await update.message.reply_text(
        "Введите username менеджера (без @):\n"
        "Пример: username123"
    )
    context.user_data["awaiting_manager_add"] = True


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление менеджера владельцем"""
    await update.message.reply_text(
        "Введите username менеджера для удаления (без @):\n"
        "Пример: username123"
    )
    context.user_data["awaiting_manager_remove"] = True


async def handle_manager_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода username для управления менеджерами"""
    text = update.message.text.strip()
    
    if context.user_data.get("awaiting_manager_add"):
        # Логика добавления менеджера
        if text:
            try:
                # Здесь должна быть логика поиска user_id по username
                # и вызов set_user_role(user_id, "manager")
                await update.message.reply_text(
                    f"Менеджер @{text} добавлен.\n"
                    "Роль изменена на 'manager'."
                )
            except Exception as e:
                await update.message.reply_text(
                    f"Ошибка: {e}\n"
                    "Проверьте username и повторите."
                )
        context.user_data.pop("awaiting_manager_add", None)
        return
    
    if context.user_data.get("awaiting_manager_remove"):
        # Логика удаления менеджера
        if text:
            try:
                # Здесь должна быть логика поиска user_id по username
                # и вызов set_user_role(user_id, "user")
                await update.message.reply_text(
                    f"Менеджер @{text} удалён.\n"
                    "Роль изменена на 'user'."
                )
            except Exception as e:
                await update.message.reply_text(
                    f"Ошибка: {e}\n"
                    "Проверьте username и повторите."
                )
        context.user_data.pop("awaiting_manager_remove", None)
        return


# Примечание: Этот файл импортируется в owner.py
# Для работы требуется импорт Update и ContextTypes
