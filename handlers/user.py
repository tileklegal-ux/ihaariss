from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

# ==================================================
# КНОПКИ
# ==================================================

BTN_YES = "Да"
BTN_NO = "Нет"

BTN_BIZ = "📊 Бизнес-анализ"
BTN_PM = "💰 Прибыль и деньги"
BTN_GROWTH = "🚀 Рост и продажи"
BTN_BACK = ⬅️ Назад"

BTN_ANALYSIS = "📦 Аналитика товара"
BTN_NICHE = "🔎 Подбор ниши"
BTN_PROFILE = "👤 Личный кабинет"
BTN_PREMIUM = "❤️ Premium"

# ==================================================
# КЛАВИАТУРЫ
# ==================================================

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_BIZ)],
            [KeyboardButton(BTN_ANALYSIS)],
            [KeyboardButton(BTN_NICHE)],
            [KeyboardButton(BTN_PROFILE)],
            [KeyboardButton(BTN_PREMIUM)],
        ],
        resize_keyboard=True,
    )

def business_hub_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_PM)],
            [KeyboardButton(BTN_GROWTH)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )

def growth_channels_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📸 Instagram"), KeyboardButton("✈️ Telegram")],
            [KeyboardButton("💳 Kaspi"), KeyboardButton("📦 Wildberries")],
            [KeyboardButton("📦 Ozon"), KeyboardButton("🏬 Офлайн")],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )

# ==================================================
# /start
# ==================================================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    name = user.first_name or user.username or "друг"

    await update.message.reply_text(
        f"Привет, {name} 👋\n\n"
        "Ты в Artbazar AI — помощнике для анализа решений.\n\n"
        "Здесь нет советов и прогнозов.\n"
        "Мы разбираем логику, риски и ограничения,\n"
        "чтобы решения принимались спокойнее.\n\n"
        "⚠️ Важно:\n"
        "Результаты — ориентиры, не гарантии.\n"
        "Ответственность всегда остаётся за тобой.\n\n"
        "Продолжим?",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )

async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбери раздел 👇",
        reply_markup=main_menu_keyboard(),
    )

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хорошо. Я рядом.",
        reply_markup=main_menu_keyboard(),
    )

# ==================================================
# 📊 БИЗНЕС-АНАЛИЗ
# ==================================================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Бизнес-анализ\n\n"
        "Здесь анализ — это логика и ограничения,\n"
        "а не отчёты и графики.",
        reply_markup=business_hub_keyboard(),
    )

async def on_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Главное меню",
        reply_markup=main_menu_keyboard(),
    )

# ==================================================
# 💰 ПРИБЫЛЬ И ДЕНЬГИ (FSM)
# ==================================================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["pm_state"] = "revenue"

    await update.message.reply_text(
        "💰 Прибыль и деньги\n\n"
        "Укажи выручку за один конкретный месяц.\n"
        "Без прогнозов — только фактические поступления.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
    )

async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace(" ", "")
    if not text.isdigit():
        await update.message.reply_text("Введи число.")
        return

    if context.user_data.get("pm_state") == "revenue":
        context.user_data["revenue"] = int(text)
        context.user_data["pm_state"] = "expenses"
        await update.message.reply_text(
            "Теперь укажи расходы за этот же месяц.\n"
            "Включай всё, что платил для работы бизнеса."
        )
        return

    revenue = context.user_data["revenue"]
    expenses = int(text)
    profit = revenue - expenses
    margin = (profit / revenue * 100) if revenue else 0
    context.user_data.clear()

    await update.message.reply_text(
        f"📊 Результат за месяц:\n\n"
        f"Выручка: {revenue}\n"
        f"Расходы: {expenses}\n"
        f"Прибыль: {profit}\n"
        f"Маржа: {margin:.1f}%\n\n"
        "Это не прогноз и не оценка будущего.\n"
        "Это снимок текущего состояния.",
        reply_markup=business_hub_keyboard(),
    )

# ==================================================
# 🚀 РОСТ И ПРОДАЖИ
# ==================================================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["growth"] = True

    await update.message.reply_text(
        "🚀 Рост и продажи\n\n"
        "Мы фиксируем текущий источник клиентов.\n"
        "Без ожиданий и планов на рост.",
        reply_markup=growth_channels_keyboard(),
    )

async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = update.message.text
    context.user_data.clear()

    await update.message.reply_text(
        f"📈 Текущая картина:\n\n"
        f"Источник клиентов: {channel}\n\n"
        "Это фиксация состояния,\n"
        "а не оценка качества канала.\n\n"
        "Рост — это нагрузка и риски,\n"
        "а не просто больше заказов.",
        reply_markup=business_hub_keyboard(),
    )

# ==================================================
# ❤️ PREMIUM (FSM)
# ==================================================

PREMIUM_STATE_KEY = "premium_state"

async def premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data[PREMIUM_STATE_KEY] = True

    await update.message.reply_text(
        "❤️ Premium — больше ясности\n\n"
        "Premium не даёт ответов и не обещает результат.\n"
        "Он помогает глубже увидеть связи между решениями,\n"
        "риски и ограничения.\n\n"
        "Анализ становится спокойнее и последовательнее.\n\n"
        "Premium не снимает неопределённость —\n"
        "он делает её более видимой.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("⬅️ В меню")]],
            resize_keyboard=True
        )
    )

# ==================================================
# ПРОЧЕЕ
# ==================================================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Личный кабинет\n\nИстория появится позже.",
        reply_markup=main_menu_keyboard(),
    )

# ==================================================
# ROUTER
# ==================================================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get("pm_state"):
        return await pm_handler(update, context)

    if context.user_data.get("growth"):
        return await growth_handler(update, context)

    if context.user_data.get(PREMIUM_STATE_KEY):
        context.user_data.clear()
        return await update.message.reply_text(
            "Главное меню",
            reply_markup=main_menu_keyboard(),
        )

# ==================================================
# REGISTER
# ==================================================

def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PM}$"), pm_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_GROWTH}$"), growth_start))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), premium_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), on_back))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
