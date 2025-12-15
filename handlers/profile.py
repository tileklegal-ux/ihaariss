# -*- coding: utf-8 -*-

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes

from handlers.user_helpers import get_results_summary
from handlers.user_keyboards import (
    main_menu_keyboard,
    BTN_BACK,
    BTN_DOCS,
)

from services.export_excel import build_excel_report
from services.export_pdf import build_pdf_report

# Premium — single source of truth
from services.premium_checker import is_premium_user


CHANNEL_URL = "https://t.me/artba3ar"


def channel_inline_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔔 Подписаться на канал ArtBazar.AI", url=CHANNEL_URL)]]
    )


# ==================================================
# 👤 ЛИЧНЫЙ КАБИНЕТ
# ==================================================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = context.user_data

    # Premium status
    premium_now = bool(is_premium_user(user_id))
    user_data["is_premium"] = premium_now

    history = user_data.get("history", [])

    # ------------------------------
    # 🆓 FREE
    # ------------------------------
    if not premium_now:
        summary = get_results_summary(context)

        lines = [
            "👤 Личный кабинет",
            "",
            "Тариф: FREE",
            "",
            "Что уже сделано:",
        ]

        if not summary:
            lines.append("— пока нет завершённых анализов")
        else:
            for k, v in summary.items():
                lines.append(f"— {k}: {v}")

        lines.extend([
            "",
            "В Premium доступны:",
            "• история результатов",
            "• экспорт отчётов в PDF и Excel",
        ])

        # ✅ ВАЖНО: reply-кнопки показываем в ЭТОМ ЖЕ сообщении (не пустым вторым)
        await update.message.reply_text(
            "\n".join(lines),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("❤️ Что даёт Premium")],
                    [KeyboardButton(BTN_DOCS)],
                    [KeyboardButton(BTN_BACK)],
                ],
                resize_keyboard=True,
            ),
        )

        # ✅ Канал — отдельным сообщением с inline (не ломает reply-клаву)
        await update.message.reply_text(
            "Подписывайся на канал — там разборы ниш, кейсы и обновления 👇",
            reply_markup=channel_inline_keyboard(),
        )
        return

    # ------------------------------
    # ⭐ PREMIUM
    # ------------------------------
    lines = [
        "👤 Личный кабинет",
        "",
        "Тариф: PREMIUM ⭐",
        "",
        "Последние результаты:",
    ]

    if not history:
        lines.append("— пока нет данных для отчётов")
    else:
        for item in history[-5:]:
            tpe = item.get("type", "—")
            d = item.get("date", "")
            s = item.get("summary", "")
            lines.append(f"• {tpe} | {d} | {s}")

    lines.extend([
        "",
        "📤 Экспорт отчётов:",
        "• PDF — краткий отчёт, удобно читать и отправлять",
        "• Excel — таблица для анализа и работы с цифрами",
    ])

    # ✅ Кнопки PDF/Excel — в том же сообщении, чтобы Telegram не «съел»
    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("📄 Скачать PDF"), KeyboardButton("📊 Скачать Excel")],
                [KeyboardButton(BTN_DOCS)],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        ),
    )

    # ✅ Канал — отдельным сообщением с inline
    await update.message.reply_text(
        "Подписывайся на канал — там разборы ниш, кейсы и обновления 👇",
        reply_markup=channel_inline_keyboard(),
    )


# ==================================================
# 📊 EXCEL EXPORT
# ==================================================

async def on_export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # защита экспорта
    if not is_premium_user(user_id):
        await update.message.reply_text("Экспорт доступен только в Premium.", reply_markup=main_menu_keyboard())
        return

    history = context.user_data.get("history", [])

    if not history:
        await update.message.reply_text("Нет данных для экспорта.", reply_markup=main_menu_keyboard())
        return

    stream = build_excel_report(history)

    await update.message.reply_document(
        document=stream,
        filename="artbazar_report.xlsx",
        caption="📊 Excel — таблица с твоими результатами",
        reply_markup=main_menu_keyboard(),
    )


# ==================================================
# 📄 PDF EXPORT
# ==================================================

async def on_export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # защита экспорта
    if not is_premium_user(user_id):
        await update.message.reply_text("Экспорт доступен только в Premium.", reply_markup=main_menu_keyboard())
        return

    history = context.user_data.get("history", [])

    if not history:
        await update.message.reply_text("Нет данных для экспорта.", reply_markup=main_menu_keyboard())
        return

    stream = build_pdf_report(history)

    await update.message.reply_document(
        document=stream,
        filename="artbazar_report.pdf",
        caption="📄 PDF — краткий отчёт по твоим анализам",
        reply_markup=main_menu_keyboard(),
    )
