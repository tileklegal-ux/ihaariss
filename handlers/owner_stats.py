from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_connection


async def show_owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'manager'")
    managers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'owner'")
    owners = cur.fetchone()[0]

    conn.close()

    await update.message.reply_text(
        f"📊 Статистика:\n"
        f"Всего пользователей: {total_users}\n"
        f"Владельцев: {owners}\n"
        f"Менеджеров: {managers}"
    )
