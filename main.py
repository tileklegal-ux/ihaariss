import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_TOKEN
from database.db import get_user_role, ensure_user_exists, get_user

from handlers.user import cmd_start_user, register_handlers_user
from handlers.owner import owner_start, register_handlers_owner
from handlers.manager import manager_start, register_handlers_manager
from handlers.role_actions import register_role_actions


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    logger.info(f"📨 /start from user_id={user_id}, username=@{username}")
    
    ensure_user_exists(user_id, username)
    
    user_data = get_user(user_id)
    logger.info(f"📊 User data from DB: {user_data}")
    
    role = get_user_role(user_id)
    logger.info(f"🎭 User role: {role}")
    
    if role == "owner":
        logger.info(f"👑 Routing to owner panel")
        await owner_start(update, context)
        return

    if role == "manager":
        logger.info(f"👨‍💼 Routing to manager panel")
        await manager_start(update, context)
        return

    logger.info(f"👤 Routing to user panel")
    await cmd_start_user(update, context)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_router), group=0)

    register_role_actions(app)        # group 1 - FSM для owner/manager
    register_handlers_owner(app)      # group 2 - кнопки владельца  
    register_handlers_manager(app)    # group 3 - кнопки менеджера
    register_handlers_user(app)       # group 4 - пользователь

    logger.info("🚀 Bot started and polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
