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
BTN_ANALYSIS = "📦 Аналитика товара"
BTN_NICHE = "🔎 Подбор ниши"
BTN_PROFILE = "👤 Личный кабинет"
BTN_PREMIUM = "❤️ Premium"
BTN_BACK = "⬅️ Назад"

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

# ==================================================
# START
# ==================================================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    name = update.effective_user.first_name or "друг"

    await update.message.reply_text(
        f"Привет, {name} 👋\n\n"
        "Artbazar AI помогает разложить бизнес-решения по полочкам\n"
        "и снизить неопределённость.\n\n"
        "Это не советы и не прогнозы.\n"
        "Решения всегда остаются за тобой.\n\n"
        "Продолжим?",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )

async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери раздел 👇", reply_markup=main_menu_keyboard())

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я рядом.", reply_markup=main_menu_keyboard())

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
    await update.message.reply_text("Главное меню", reply_markup=main_menu_keyboard())

# ==================================================
# 💰 ПРИБЫЛЬ И ДЕНЬГИ (FSM)
# ==================================================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["pm_state"] = "revenue"

    await update.message.reply_text(
        "💰 Прибыль и деньги\n\n"
        "Укажи выручку за месяц.\n"
        "Без прогнозов — только факт.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
    )

async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace(" ", "")
    if not text.isdigit():
        await update.message.reply_text("Введи число.")
        return

    if context.user_data["pm_state"] == "revenue":
        context.user_data["revenue"] = int(text)
        context.user_data["pm_state"] = "expenses"
        await update.message.reply_text("Теперь укажи расходы за этот же месяц.")
        return

    revenue = context.user_data["revenue"]
    expenses = int(text)
    profit = revenue - expenses
    margin = (profit / revenue * 100) if revenue else 0
    context.user_data.clear()

    await update.message.reply_text(
        f"Результат за месяц:\n\n"
        f"Прибыль: {profit}\n"
        f"Маржа: {margin:.1f}%\n\n"
        "Это снимок состояния, не прогноз.",
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
        "Откуда клиенты приходят сейчас?",
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("📸 Instagram"), KeyboardButton("✈️ Telegram")],
                [KeyboardButton("💳 Kaspi"), KeyboardButton("📦 Wildberries")],
                [KeyboardButton("📦 Ozon"), KeyboardButton("🏬 Офлайн")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        ),
    )

async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = update.message.text
    context.user_data.clear()

    await update.message.reply_text(
        f"Источник: {channel}\n\n"
        "Это фиксация текущего состояния.\n"
        "Рост — это нагрузка на систему.",
        reply_markup=business_hub_keyboard(),
    )

# ==================================================
# 📦 АНАЛИТИКА ТОВАРА (FSM)
# ==================================================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["ta_step"] = 1

    await update.message.reply_text(
        "📦 Аналитика товара\n\n"
        "На какой стадии идея?",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["Рассматриваю товар"],
                ["Есть идея"],
                ["Изучаю рынок"],
                [BTN_BACK],
            ],
            resize_keyboard=True,
        ),
    )

async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("ta_step")

    if step == 1:
        context.user_data["ta_step"] = 2
        await update.message.reply_text("Зачем его покупают?")
        return

    if step == 2:
        context.user_data.clear()
        await update.message.reply_text(
            "Вердикт: ориентир, не рекомендация.\n"
            "Следующий шаг — аккуратная проверка.",
            reply_markup=main_menu_keyboard(),
        )

# ==================================================
# 🔎 ПОДБОР НИШИ (FSM)
# ==================================================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["ns_step"] = 1

    await update.message.reply_text(
        "🔎 Подбор ниши\n\n"
        "Это не выбор ниши, а проверка рамок.",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["Запуск с нуля"],
                ["Смена направления"],
                ["Изучаю рынок"],
                [BTN_BACK],
            ],
            resize_keyboard=True,
        ),
    )

async def ns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Результат — ориентир.\n"
        "Решение остаётся за тобой.",
        reply_markup=main_menu_keyboard(),
    )

# ==================================================
# ПРОЧЕЕ
# ==================================================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("История появится позже.", reply_markup=main_menu_keyboard())

async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Premium даёт больше ясности.\n"
        "Без обещаний результата.",
        reply_markup=main_menu_keyboard(),
    )

# ==================================================
# ROUTER
# ==================================================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("pm_state"):
        return await pm_handler(update, context)
    if context.user_data.get("growth"):
        return await growth_handler(update, context)
    if context.user_data.get("ta_step"):
        return await ta_handler(update, context)
    if context.user_data.get("ns_step"):
        return await ns_handler(update, context)

# ==================================================
# REGISTER
# ==================================================

def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PM}$"), pm_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_GROWTH}$"), growth_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NICHE}$"), ns_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), on_premium))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), on_back))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
