# handlers/owner_stats.py
from telegram import Update
from telegram.ext import ContextTypes
from contextlib import closing

from database.db import get_connection


async def show_owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with closing(get_connection()) as conn:
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM users")
        total_users = int(cur.fetchone()[0] or 0)

        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'manager'")
        managers = int(cur.fetchone()[0] or 0)

        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'owner'")
        owners = int(cur.fetchone()[0] or 0)

        cur.execute("SELECT COUNT(*) FROM users WHERE premium_until > 0")
        premium_any = int(cur.fetchone()[0] or 0)

    text = (
        "📊 Общая статистика\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"👑 Владельцев: {owners}\n"
        f"🧑‍💼 Менеджеров: {managers}\n"
        f"⭐ Premium (всего записей): {premium_any}"
    )

    await update.message.reply_text(text)
