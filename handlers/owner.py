# handlers/owner.py - обновленный текстовый роутер

async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        return

    text = update.message.text or ""

    if text == BTN_OWNER_STATS:
        await show_owner_stats(update, context)
        return

    if text == BTN_ADD_MANAGER:
        await add_manager(update, context)  # Теперь это запускает FSM
        return

    if text == BTN_REMOVE_MANAGER:
        await remove_manager(update, context)  # Теперь это запускает FSM
        return

    if text == BTN_EXIT:
        # Сбрасываем все состояния
        context.user_data.clear()
        await update.message.reply_text("Выход из панели владельца.")
        return
