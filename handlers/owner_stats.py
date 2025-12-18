# handlers/owner_stats.py

from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_connection


async def show_owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'manager'")
        managers = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE premium_until > strftime('%s','now')")
        premium_users = cur.fetchone()[0]

    text = (
        "📊 Общая статистика\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"🧑‍💼 Менеджеров: {managers}\n"
        f"❤️ Premium пользователей: {premium_users}"
    )

    await update.message.reply_text(text)
