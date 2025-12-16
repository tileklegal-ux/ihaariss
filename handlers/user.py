# handlers/user.py
# -*- coding: utf-8 -*-

import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
    Application,
)

from handlers.user_keyboards import (
    BTN_AI_CHAT,
    BTN_EXIT_CHAT,
    ai_chat_keyboard,
    main_menu_keyboard,
    business_hub_keyboard,
    growth_channels_keyboard,
    step_keyboard,
    premium_keyboard,
    BTN_YES,
    BTN_NO,
    BTN_BACK,
    BTN_BIZ,
    BTN_PM,
    BTN_GROWTH,
    BTN_ANALYSIS,
    BTN_NICHE,
    BTN_PROFILE,
    BTN_PREMIUM,
    BTN_PREMIUM_BENEFITS,
)

from handlers.user_texts import t
from handlers.user_helpers import (
    clear_fsm,
    save_insights,
    insights_bridge_text,
)

from handlers.profile import on_profile, on_export_excel, on_export_pdf
from handlers.documents import on_documents

from services.openai_client import ask_openai
from database.db import (
    is_user_premium,
    get_user_role,
)

logger = logging.getLogger(__name__)

# =============================
# FSM KEYS / STATES
# =============================
PM_STATE_KEY = "pm_state"
PM_STATE_REVENUE = "pm_revenue"
PM_STATE_EXPENSES = "pm_expenses"

GROWTH_KEY = "growth"

TA_STATE_KEY = "ta_state"
TA_STAGE = "ta_stage"
TA_PURPOSE = "ta_purpose"
TA_SEASON = "ta_season"
TA_COMP = "ta_comp"
TA_PRICE = "ta_price"
TA_RESOURCE = "ta_resource"

NS_STEP_KEY = "ns_step"

PREMIUM_KEY = "is_premium"
AI_CHAT_MODE_KEY = "ai_chat_mode"
ONBOARDING_KEY = "onboarding"

# =============================
# START / ONBOARDING
# =============================
async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data.pop(AI_CHAT_MODE_KEY, None)

    if "lang" not in context.user_data:
        context.user_data["lang"] = "ru"

    context.user_data[ONBOARDING_KEY] = True

    user = update.effective_user
    name = user.first_name or user.username or "друг"
    lang = context.user_data["lang"]

    await update.message.reply_text(
        t(lang, "start_greeting", name=name),
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )

async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(ONBOARDING_KEY, None)
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        t(lang, "choose_section"),
        reply_markup=main_menu_keyboard(),
    )

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(ONBOARDING_KEY, None)
    await update.message.reply_text(
        "Хорошо. Я рядом.",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# 📊 БИЗНЕС-АНАЛИЗ (ХАБ)
# =============================
async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        t(lang, "business_hub_intro"),
        reply_markup=business_hub_keyboard(),
    )

# =============================
# 💰 ПРИБЫЛЬ И ДЕНЬГИ
# =============================
async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[PM_STATE_KEY] = PM_STATE_REVENUE
    bridge = insights_bridge_text(context)

    await update.message.reply_text(
        bridge +
        "💰 Прибыль и деньги\n\n"
        "Укажи выручку за выбранный месяц.\n"
        "Сколько денег фактически поступило от клиентов.\n"
        "Без прогнозов и ожиданий — только реальные поступления.\n"
        "Период важен: считаем один конкретный месяц.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True,
        ),
    )

async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_raw = update.message.text or ""
    text = text_raw.replace(" ", "").replace(",", "").strip()

    if not text.isdigit():
        await update.message.reply_text("Введи число, без букв.")
        return

    state = context.user_data.get(PM_STATE_KEY)

    if state == PM_STATE_REVENUE:
        context.user_data["revenue"] = int(text)
        context.user_data[PM_STATE_KEY] = PM_STATE_EXPENSES
        await update.message.reply_text(
            "Теперь укажи расходы за этот же месяц.\n"
            "Закупки, реклама, аренда, сервисы, комиссии.\n"
            "Если сомневаешься — лучше завысить, чем забыть.\n"
            "Нужна общая сумма."
        )
        return

    if state == PM_STATE_EXPENSES:
        revenue = context.user_data.get("revenue", 0)
        expenses = int(text)
        profit = revenue - expenses
        margin = (profit / revenue * 100) if revenue else 0

        risk_level = "средний"
        if revenue == 0 or profit < 0:
            risk_level = "высокий"
        elif margin >= 10:
            risk_level = "низкий"

        last_verdict = "Осторожно"
        if margin >= 10:
            last_verdict = "Можно смотреть"
        if profit < 0:
            last_verdict = "Высокий риск"

        save_insights(
            context,
            last_scenario="💰 Деньги",
            last_verdict=last_verdict,
            risk_level=risk_level,
        )

        clear_fsm(context)

        base_text = (
            "Итог за месяц:\n\n"
            f"Выручка: {revenue}\n"
            f"Расходы: {expenses}\n"
            f"Прибыль: {profit}\n"
            f"Маржа: {margin:.1f}%\n"
        )

        ai_prompt = (
            "Сделай короткий аналитический комментарий по месячной модели.\n"
            "Запрещено: советы, обещания, прогнозы, директивы.\n"
            "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"Данные: выручка={revenue}, расходы={expenses}, прибыль={profit}, маржа%={margin:.1f}."
        )

        ai_text = await ask_openai(ai_prompt)

        await update.message.reply_text(
            base_text + "\nКороткий разбор:\n" + ai_text,
            reply_markup=business_hub_keyboard(),
        )

# =============================
# 🚀 РОСТ И ПРОДАЖИ
# =============================
async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[GROWTH_KEY] = True
    bridge = insights_bridge_text(context)

    await update.message.reply_text(
        bridge +
        "🚀 Рост и продажи\n\n"
        "Мы просто фиксируем текущий канал.\n"
        "Без оценки эффективности.\n\n"
        "Выбери источник клиентов:",
        reply_markup=growth_channels_keyboard(),
    )

async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = update.message.text or ""

    save_insights(
        context,
        last_scenario="🚀 Рост",
        last_verdict="Канал зафиксирован",
    )

    clear_fsm(context)

    await update.message.reply_text(
        f"Источник клиентов: {channel}\n\n"
        "Это фиксация текущего состояния.",
        reply_markup=business_hub_keyboard(),
    )

# =============================
# ❤️ PREMIUM
# =============================
async def premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)

    OFFER_URL = "https://www.notion.so/Premium-2c901cd07aa7808b85ddec9d8019e742?source=copy_link"

    text = (
        "❤️ Premium\n\n"
        "Подключение через менеджера:\n"
        "@Artbazar_marketing\n\n"
        "После активации доступны:\n"
        "• AI-чат\n"
        "• история анализов\n"
        "• экспорт PDF / Excel"
    )

    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📄 Публичная оферта", url=OFFER_URL)]]
    )

    await update.message.reply_text(text, reply_markup=kb)
    await update.message.reply_text(" ", reply_markup=premium_keyboard())

async def premium_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Возможности Premium:\n\n"
        "• AI-чат\n"
        "• история состояний\n"
        "• экспорт отчётов",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True,
        ),
    )

# =============================
# 💬 AI CHAT
# =============================
async def enter_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)

    if not is_user_premium(update.effective_user.id):
        await update.message.reply_text(
            "💬 AI-чат доступен только для Premium.\n\n"
            "Подключите Premium, чтобы продолжить.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(BTN_BACK)]],
                resize_keyboard=True,
            ),
        )
        return

    context.user_data[AI_CHAT_MODE_KEY] = True

    await update.message.reply_text(
        "💬 AI-чат (Premium)\n\n"
        "Напишите сообщение.\n"
        "Для выхода нажмите «Назад».",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True,
        ),
    )

async def ai_chat_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = (update.message.text or "").strip()

    if not user_text:
        return

    if not is_user_premium(update.effective_user.id):
        return

    try:
        await update.message.chat.send_action("typing")
        answer = await ask_openai(user_text)
        await update.message.reply_text(answer)
    except Exception:
        await update.message.reply_text("⚠️ Ошибка AI. Попробуй позже.")

# =============================
# ROUTER — TEXT
# =============================
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or ""

    if user_text.startswith("/"):
        return

    # 🔒 ЖЁСТКАЯ ИЗОЛЯЦИЯ РОЛЕЙ
    try:
        role = get_user_role(update.effective_user.id)
    except Exception:
        return

    if role != "user":
        return

    # AI chat button
    if user_text == BTN_AI_CHAT:
        await enter_ai_chat(update, context)
        return

    if user_text == BTN_YES:
        await on_yes(update, context)
        return

    if user_text == BTN_NO:
        await on_no(update, context)
        return

    if user_text == BTN_BACK:
        context.user_data.pop(AI_CHAT_MODE_KEY, None)
        clear_fsm(context)
        await update.message.reply_text(
            "Главное меню",
            reply_markup=main_menu_keyboard(),
        )
        return

    if context.user_data.get(AI_CHAT_MODE_KEY):
        await ai_chat_text_handler(update, context)
        return

    if user_text == BTN_BIZ:
        await on_business_analysis(update, context)
        return

    if user_text == BTN_PM:
        await pm_start(update, context)
        return

    if user_text == BTN_GROWTH:
        await growth_start(update, context)
        return

    if user_text == BTN_PROFILE:
        await on_profile(update, context)
        return

    if user_text == BTN_PREMIUM:
        await premium_start(update, context)
        return

    if user_text == BTN_PREMIUM_BENEFITS:
        await premium_benefits(update, context)
        return

    if user_text == "📄 Скачать PDF":
        await on_export_pdf(update, context)
        return

    if user_text == "📊 Скачать Excel":
        await on_export_excel(update, context)
        return

    if user_text in ("📄 Документы", "📄 Документы и условия"):
        await on_documents(update, context)
        return

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        t(lang, "choose_section"),
        reply_markup=main_menu_keyboard(),
    )

# =============================
# REGISTER
# =============================
def register_handlers_user(app: Application):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_router),
        group=4,
    )
