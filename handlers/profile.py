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
from handlers.user_keyboards import BTN_BACK
from handlers.user_texts import t

from services.export_excel import build_excel_report
from services.export_pdf import build_pdf_report
from services.premium_checker import is_premium_user


CHANNEL_URL = "https://t.me/artba3ar"


def channel_inline():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔔 Подписаться на канал ArtBazar.ai", url=CHANNEL_URL)]]
    )


async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ru")
    premium = bool(is_premium_user(user_id))
    history = context.user_data.get("history", [])

    # ---------- FREE ----------
    if not premium:
        summary = get_results_summary(context)

        text = [
            "👤 Личный кабинет",
            "",
            "Тариф: FREE",
            "",
            "Что уже сделано:",
        ]

        if not summary:
            text.append("— пока нет завершённых анализов")
        else:
            for k, v in summary.items():
                text.append(f"— {k}: {v}")

        text += [
            "",
            "В Premium доступно:",
            "• история результатов",
            "• экспорт PDF / Excel",
        ]

        await update.message.reply_text(
            "\n".join(text),
            reply_markup=channel_inline(),
        )

        await update.message.reply_text(
            " ",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("❤️ Что даёт Premium")],
                    [KeyboardButton("📄 Документы и условия")],
                    [KeyboardButton(BTN_BACK)],
                ],
                resize_keyboard=True,
            ),
        )
        return

    # ---------- PREMIUM ----------
    text = [
        "👤 Личный кабинет",
        "",
        "Тариф: PREMIUM ⭐",
        "",
        "Последние результаты:",
    ]

    if not history:
        text.append("— пока нет данных")
    else:
        for item in history[-5:]:
            text.append(
                f"• {item.get('type','')} | {item.get('date','')} | {item.get('summary','')}"
            )

    text += [
        "",
        "📤 Экспорт отчётов:",
        "PDF — краткий отчёт",
        "Excel — таблица с данными",
    ]

    await update.message.reply_text(
        "\n".join(text),
        reply_markup=channel_inline(),
    )

    await update.message.reply_text(
        " ",
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("📄 Скачать PDF"), KeyboardButton("📊 Скачать Excel")],
                [KeyboardButton("📄 Документы и условия")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        ),
    )


# ---------- EXPORT ----------

async def on_export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_premium_user(update.effective_user.id):
        return

    history = context.user_data.get("history", [])
    if not history:
        return

    stream = build_excel_report(history)
    await update.message.reply_document(stream, filename="artbazar.xlsx")


async def on_export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_premium_user(update.effective_user.id):
        return

    history = context.user_data.get("history", [])
    if not history:
        return

    stream = build_pdf_report(history)
    await update.message.reply_document(stream, filename="artbazar.pdf")
