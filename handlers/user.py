from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)

# =============================
# КНОПКИ
# =============================

BTN_YES = "Да"
BTN_NO = "Нет"

BTN_BIZ = "📊 Бизнес-анализ"
BTN_PM = "💰 Прибыль и деньги"
BTN_GROWTH = "🚀 Рост и продажи"
BTN_BACK = "⬅️ Назад"

BTN_ANALYSIS = "📊 Аналитика товара"
BTN_NICHE = "🔎 Подбор ниши"
BTN_PROFILE = "👤 Личный кабинет"
BTN_PREMIUM = "❤️ Премиум"


# =============================
# КЛАВИАТУРЫ
# =============================

def get_main_menu_keyboard():
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


# =============================
# START FLOW
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or user.username or "друг"

    text = (
        f"Привет, {name} 👋\n\n"
        "Тебя приветствует Artbazar AI — аналитический помощник для предпринимателей.\n\n"
        "⚠️ Важно: аналитика — это поддержка решений, а не гарантия результата.\n\n"
        "Продолжим?"
    )

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )


async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбери раздел 👇",
        reply_markup=get_main_menu_keyboard(),
    )


async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хорошо. Я рядом.",
        reply_markup=get_main_menu_keyboard(),
    )


# =============================
# БИЗНЕС-АНАЛИЗ HUB
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Бизнес-анализ\n\nВыбери сценарий:",
        reply_markup=business_hub_keyboard(),
    )


async def on_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Главное меню",
        reply_markup=get_main_menu_keyboard(),
    )


# =============================
# FSM 💰 ПРИБЫЛЬ И ДЕНЬГИ
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["pm_state"] = "revenue"

    await update.message.reply_text(
        "💰 Прибыль и деньги\n\n"
        "Введи *выручку в месяц* (число):",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True,
        ),
    )


async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("pm_state")
    text = update.message.text.replace(" ", "")

    if state == "revenue":
        if not text.isdigit():
            await update.message.reply_text("Введи число.")
            return

        context.user_data["revenue"] = int(text)
        context.user_data["pm_state"] = "expenses"

        await update.message.reply_text(
            "Теперь введи *расходы в месяц*:",
            parse_mode="Markdown",
        )
        return

    if state == "expenses":
        if not text.isdigit():
            await update.message.reply_text("Введи число.")
            return

        revenue = context.user_data["revenue"]
        expenses = int(text)

        profit = revenue - expenses
        margin = (profit / revenue * 100) if revenue > 0 else 0

        result = (
            "📊 *Результат расчёта:*\n\n"
            f"Выручка: {revenue}\n"
            f"Расходы: {expenses}\n"
            f"Прибыль: {profit}\n"
            f"Маржа: {margin:.1f}%\n\n"
            "Это базовый ориентир, а не финансовый совет."
        )

        context.user_data.clear()

        await update.message.reply_text(
            result,
            parse_mode="Markdown",
            reply_markup=business_hub_keyboard(),
        )


# =============================
# ДРУГИЕ РАЗДЕЛЫ (ПОКА ЗАГЛУШКИ)
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Рост и продажи\n\nБудет подключено позже.",
        reply_markup=business_hub_keyboard(),
    )


async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Аналитика товара\n\nБудет подключена позже.",
        reply_markup=get_main_menu_keyboard(),
    )


async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 Подбор ниши\n\nБудет подключён позже.",
        reply_markup=get_main_menu_keyboard(),
    )


async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Личный кабинет\n\nПоявится после первых расчётов.",
        reply_markup=get_main_menu_keyboard(),
    )


async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ Premium\n\nПодключение позже.",
        reply_markup=get_main_menu_keyboard(),
    )


# =============================
# REGISTER
# =============================

def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PM}$"), pm_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), on_back))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, pm_handler))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_GROWTH}$"), growth_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NICHE}$"), ns_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), on_premium))
