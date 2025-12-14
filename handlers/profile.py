# -*- coding: utf-8 -*-
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from handlers.user_helpers import get_results_summary
from handlers.user_keyboards import (
    main_menu_keyboard,
    BTN_PREMIUM,
    BTN_BACK,
)

# ==================================================
# 👤 ЛИЧНЫЙ КАБИНЕТ
# ==================================================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data

    is_premium = user_data.get("is_premium", False)
    history = user_data.get("history", [])

    # ------------------------------
    # 🆓 FREE
    # ------------------------------
    if not is_premium:
        summary = get_results_summary(context)

        lines = [
            "👤 Личный кабинет",
            "",
            "Статус: 🆓 Базовый доступ",
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
            "Ты можешь анализировать идеи и риски.",
            "В Premium доступны отчёты, история и выгрузка в PDF / Excel.",
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

    # ------------------------------
    # ⭐ PREMIUM
    # ------------------------------
    lines = [
        "👤 Личный кабинет",
        "",
        "Статус: ⭐ Premium активен",
        "",
        "Последние результаты:",
    ]

    if not history:
        lines.append("— нет данных для отчётов")
    else:
        for item in history[-5:]:
            t = item.get("type", "—")
            d = item.get("date", "")
            s = item.get("summary", "")
            lines.append(f"• {t} | {d} | {s}")

    lines.extend([
        "",
        "Экспорт:",
    ])

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("📄 Скачать PDF"), KeyboardButton("📊 Скачать Excel")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        ),
    )
