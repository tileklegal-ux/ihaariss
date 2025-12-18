from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters, Application

from database.db import (
    get_user_by_username, 
    set_role_by_telegram_id, 
    give_premium_days, 
    get_user_role,
    get_user
)

# =============================
# КОНСТАНТЫ КНОПОК
# =============================
BTN_GIVE_PREMIUM = "📋 Выдать Premium"
BTN_EXIT = "⬅️ Выйти"

# =============================
# КЛЮЧИ FSM
# =============================
ADD_MANAGER_STATE = "add_manager_state"
REMOVE_MANAGER_STATE = "remove_manager_state"
GIVE_PREMIUM_STATE = "give_premium_state"
EXPECTING_USERNAME = "expecting_username"
EXPECTING_DAYS = "expecting_days"

# =============================
# FSM ФУНКЦИИ ДЛЯ ВЛАДЕЛЬЦА
# =============================

async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало FSM для добавления менеджера"""
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        return
    
    context.user_data[ADD_MANAGER_STATE] = True
    await update.message.reply_text(
        "Введите @username нового менеджера (без @):",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )


async def add_manager_username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка username для добавления менеджера"""
    text = update.message.text.strip()
    
    if text == "❌ Отмена":
        context.user_data.clear()
        from handlers.owner import owner_keyboard
        await update.message.reply_text("Действие отменено.", reply_markup=owner_keyboard())
        return
    
    # Ищем пользователя по username
    user = get_user_by_username(text)
    if not user:
        await update.message.reply_text(f"Пользователь @{text} не найден. Попробуйте еще раз:")
        return
    
    # Назначаем роль менеджера
    set_role_by_telegram_id(user["telegram_id"], "manager")
    
    context.user_data.clear()
    from handlers.owner import owner_keyboard
    await update.message.reply_text(
        f"✅ Пользователь @{text} теперь менеджер.",
        reply_markup=owner_keyboard()
    )


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало FSM для удаления менеджера"""
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        return
    
    context.user_data[REMOVE_MANAGER_STATE] = True
    await update.message.reply_text(
        "Введите @username менеджера для удаления (без @):",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )


async def remove_manager_username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка username для удаления менеджера"""
    text = update.message.text.strip()
    
    if text == "❌ Отмена":
        context.user_data.clear()
        from handlers.owner import owner_keyboard
        await update.message.reply_text("Действие отменено.", reply_markup=owner_keyboard())
        return
    
    # Ищем пользователя по username
    user = get_user_by_username(text)
    if not user:
        await update.message.reply_text(f"Пользователь @{text} не найден. Попробуйте еще раз:")
        return
    
    # Меняем роль на user
    set_role_by_telegram_id(user["telegram_id"], "user")
    
    context.user_data.clear()
    from handlers.owner import owner_keyboard
    await update.message.reply_text(
        f"✅ Пользователь @{text} больше не менеджер.",
        reply_markup=owner_keyboard()
    )


# =============================
# FSM ФУНКЦИИ ДЛЯ МЕНЕДЖЕРА
# =============================

async def give_premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало FSM для выдачи Premium"""
    role = get_user_role(update.effective_user.id)
    if role not in ("manager", "owner"):
        return
    
    context.user_data[GIVE_PREMIUM_STATE] = True
    context.user_data[EXPECTING_USERNAME] = True
    
    await update.message.reply_text(
        "Введите @username пользователя для выдачи Premium (без @):",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )


async def give_premium_username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка username для выдачи Premium"""
    text = update.message.text.strip()
    
    if text == "❌ Отмена":
        context.user_data.clear()
        from handlers.manager import manager_keyboard
        await update.message.reply_text("Действие отменено.", reply_markup=manager_keyboard())
        return
    
    # Ищем пользователя
    user = get_user_by_username(text)
    if not user:
        await update.message.reply_text(f"Пользователь @{text} не найден. Попробуйте еще раз:")
        return
    
    context.user_data["target_user_id"] = user["telegram_id"]
    context.user_data["target_username"] = text
    context.user_data[EXPECTING_USERNAME] = False
    context.user_data[EXPECTING_DAYS] = True
    
    await update.message.reply_text(
        f"Пользователь @{text} найден.\n"
        f"Введите количество дней Premium (1-365):",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )


async def give_premium_days_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка количества дней для Premium"""
    text = update.message.text.strip()
    
    if text == "❌ Отмена":
        context.user_data.clear()
        from handlers.manager import manager_keyboard
        await update.message.reply_text("Действие отменено.", reply_markup=manager_keyboard())
        return
    
    try:
        days = int(text)
        if not 1 <= days <= 365:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Введите корректное число дней (1-365):")
        return
    
    target_user_id = context.user_data.get("target_user_id")
    target_username = context.user_data.get("target_username", "")
    
    # Выдаем Premium
    give_premium_days(target_user_id, days)
    
    context.user_data.clear()
    from handlers.manager import manager_keyboard
    await update.message.reply_text(
        f"✅ Пользователю @{target_username} выдан Premium на {days} дней.",
        reply_markup=manager_keyboard()
    )


# =============================
# РОУТЕР ДЛЯ FSM СОСТОЯНИЙ
# =============================

async def role_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Роутер текстовых сообщений для владельца и менеджера - ТОЛЬКО FSM"""
    text = update.message.text or ""
    
    # Роутинг по состоянию FSM
    if context.user_data.get(ADD_MANAGER_STATE):
        await add_manager_username_handler(update, context)
        return
    
    if context.user_data.get(REMOVE_MANAGER_STATE):
        await remove_manager_username_handler(update, context)
        return
    
    if context.user_data.get(GIVE_PREMIUM_STATE):
        if context.user_data.get(EXPECTING_USERNAME):
            await give_premium_username_handler(update, context)
            return
        elif context.user_data.get(EXPECTING_DAYS):
            await give_premium_days_handler(update, context)
            return
    
    # ЕСЛИ НЕТ АКТИВНОГО FSM СОСТОЯНИЯ - ВЫХОДИМ И ПЕРЕДАЕМ УПРАВЛЕНИЕ
    return


# =============================
# РЕГИСТРАЦИЯ HANDLERS
# =============================

def register_role_actions(app: Application):
    """Регистрирует FSM-обработчики для владельца и менеджера в группе 1"""
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, role_text_router),
        group=1,  # ПЕРВАЯ группа - перед обычными кнопками
    )
