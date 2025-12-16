# handlers/owner.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)

from database.db import (
    get_user_by_username,
    set_role_by_telegram_id,
    get_stats,
    get_user_role,
)

from handlers.user_keyboards import main_menu_keyboard # <--- Оставим импорт для примера

# ==================================================
# OWNER KEYBOARDS
# ==================================================

# 📌 ФИКС: Изменение текста кнопки для соответствия логике:
# Теперь эта кнопка вызывает open_owner_menu, т.е. возвращает в главный раздел панели
OWNER_MENU = ReplyKeyboardMarkup(
    [
        ["➕ Добавить менеджера", "➖ Удалить менеджера"],
        ["📊 Статистика"],
        ["⬅️ Главный раздел"], # <--- ИЗМЕНЕН ТЕКСТ КНОПКИ
    ],
    resize_keyboard=True,
)

OWNER_START_KB = ReplyKeyboardMarkup(
    [["👑 Панель владельца"]],
    resize_keyboard=True,
)

# ==================================================
# TEXTS
# ==================================================
# ... (Остальной текст без изменений) ...


# ==================================================
# OWNER ENTRY
# ==================================================

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
# ... (функция без изменений) ...

# ==================================================
# OWNER MAIN MENU
# ==================================================

async def open_owner_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "owner":
        return

    context.user_data.pop("ai_chat_mode", None)
    context.user_data.pop("pm_state", None)
    context.user_data.pop("ta_state", None)
    context.user_data.pop("ns_step", None)
    context.user_data.pop("growth", None)
    context.user_data.pop("owner_mode", None)

    await update.message.reply_text(
        "👑 Панель владельца",
        reply_markup=OWNER_MENU,
    )
    # 📌 ФИКС: Возврат, чтобы предотвратить попадание в group=4 (text_router)
    return


# ==================================================
# FSM STARTERS
# ==================================================
# ... (функции без изменений) ...

# ==================================================
# STATS
# ==================================================
# ... (функции без изменений) ...

# ==================================================
# FSM HANDLER
# ==================================================
# ... (функции без изменений) ...

# ==================================================
# EXIT OWNER MODE (OLD / REMOVED)
# ==================================================

# 📌 УДАЛЕНО: Эта функция больше не нужна, так как кнопка перенаправляется на open_owner_menu.
# Для полного выхода из панели нужна отдельная, явно названная кнопка, 
# если это функциональность действительно требуется.
# async def exit_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     context.user_data.pop("owner_mode", None)
#     context.user_data.pop("ai_chat_mode", None)
#     context.user_data.pop("pm_state", None)
#     context.user_data.pop("ta_state", None)
#     context.user_data.pop("ns_step", None)
#     context.user_data.pop("growth", None)

#     await update.message.reply_text(
#         "Выход из панели владельца",
#         reply_markup=main_menu_keyboard(),
#     )
#     return 

# ==================================================
# REGISTER
# ==================================================

def register_owner_handlers(app):
    app.add_handler(
        MessageHandler(filters.Regex("^👑 Панель владельца$"), open_owner_menu),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.Regex("^➕ Добавить менеджера$"), start_add_manager),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.Regex("^➖ Удалить менеджера$"), start_remove_manager),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.Regex("^📊 Статистика$"), show_stats),
        group=1,
    )

    app.add_handler(
        # 📌 ФИКС: Кнопка "⬅️ Выйти в главное меню" теперь называется "⬅️ Главный раздел"
        # и вызывает open_owner_menu (меню владельца)
        MessageHandler(filters.Regex("^⬅️ Главный раздел$"), open_owner_menu),
        group=1,
    )
    
    # 📌 УДАЛЕНО: Хендлер на старый текст кнопки:
    # app.add_handler(
    #     MessageHandler(filters.Regex("^⬅️ Выйти в главное меню$"), exit_owner),
    #     group=1,
    # )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_owner_input),
        group=2,
    )
