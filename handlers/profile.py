# -*- coding: utf-8 -*-

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from handlers.user_helpers import get_results_summary
from handlers.user_keyboards import (
    main_menu_keyboard,
    BTN_BACK,
)
from handlers.user_texts import t

from services.export_excel import build_excel_report
from services.export_pdf import build_pdf_report

# ✅ ЕДИНЫЙ И КАНОНИЧЕСКИЙ PREMIUM-GUARD
from services.premium_checker import is_premium_user


# ==================================================
# 👤 ЛИЧНЫЙ КАБИНЕТ
# ==================================================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_id = update.effective_user.id
    lang = user_data.get("lang", "ru")

    # ------------------------------------------------
    # PREMIUM CHECK (single source of truth)
    # ------------------------------------------------
    premium_now = bool(is_premium_user(user_id))
    user_data["is_premium"] = premium_now

    history = user_data.get("history", [])

    # ==================================================
    # 🆓 FREE — ВИТРИНА PREMIUM
    # ==================================================
    if not premium_now:
        summary = get_results_summary(context)

        lines = [
            "👤 Личный кабинет",
            "",
            "Текущий тариф: FREE",
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
            "Доступно сейчас:",
            "• прохождение сценариев анализа",
            "• базовые выводы и ориентиры",
            "",
            "Недоступно в FREE:",
            "• история результатов",
            "• экспорт отчётов (PDF / Excel)",
            "",
            "⭐ В Premium:",
            "• сохранение истории анализов",
            "• скачивание отчётов в PDF",
            "• работа с данными в Excel",
        ])

        await update.message.reply_text(
            "\n".join(lines),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("❤️ Что даёт Premium")],
                    [KeyboardButton(BTN_BACK)],
                ],
                resize_keyboard=True,
            ),
        )
        return

    # ==================================================
    # ⭐ PREMIUM — ВЛАДЕНИЕ РЕЗУЛЬТАТАМИ
    # ==================================================

    lines = [
        "👤 Личный кабинет",
        "",
        "Текущий тариф: PREMIUM ⭐",
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

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=ReplyKeyboardMarkup(
            [
                [
                    KeyboardButton("📄 Скачать PDF"),
                    KeyboardButton("📊 Скачать Excel"),
                ],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        ),
    )


# ==================================================
# 📊 EXCEL EXPORT (PREMIUM ONLY)
# ==================================================

async def on_export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ru")

    # backend-защита
    if not is_premium_user(user_id):
        await update.message.reply_text(
            "Экспорт доступен только в Premium.",
            reply_markup=main_menu_keyboard(),
        )
        return

    history = context.user_data.get("history", [])

    if not history:
        await update.message.reply_text(
            t(lang, "no_data_for_export"),
            reply_markup=main_menu_keyboard(),
        )
        return

    stream = build_excel_report(history)

    await update.message.reply_document(
        document=stream,
        filename="artbazar_report.xlsx",
        caption="📊 Excel — таблица с твоими результатами",
        reply_markup=main_menu_keyboard(),
    )


# ==================================================
# 📄 PDF EXPORT (PREMIUM ONLY)
# ==================================================

async def on_export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ru")

    # backend-защита
    if not is_premium_user(user_id):
        await update.message.reply_text(
            "Экспорт доступен только в Premium.",
            reply_markup=main_menu_keyboard(),
        )
        return

    history = context.user_data.get("history", [])

    if not history:
        await update.message.reply_text(
            t(lang, "no_data_for_export"),
            reply_markup=main_menu_keyboard(),
        )
        return

    stream = build_pdf_report(history)

    await update.message.reply_document(
        document=stream,
        filename="artbazar_report.pdf",
        caption="📄 PDF — краткий отчёт по твоим анализам",
        reply_markup=main_menu_keyboard(),
    )
