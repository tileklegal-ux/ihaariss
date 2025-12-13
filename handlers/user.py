from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

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

# Каналы продаж (Рост)
BTN_CH_INST = "Instagram"
BTN_CH_TG = "Telegram"
BTN_CH_MP = "Маркетплейсы"
BTN_CH_OFFLINE = "Офлайн"
BTN_CH_OTHER = "Другое"

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


def growth_channel_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_CH_INST), KeyboardButton(BTN_CH_TG)],
            [KeyboardButton(BTN_CH_MP), KeyboardButton(BTN_CH_OFFLINE)],
            [KeyboardButton(BTN_CH_OTHER)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )

# =============================
# START FLOW (USER) — CANONICAL
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    user = update.effective_user
    name = user.first_name or user.username or "друг"

    text = (
        f"Привет, {name} 👋\n\n"
        "Тебя приветствует Artbazar AI — "
        "аналитический помощник для предпринимателей.\n\n"
        "Я помогаю:\n"
        "• проверять идеи и товары\n"
        "• считать экономику\n"
        "• выбирать ниши\n"
        "• снижать риск ошибок\n\n"
        "⚠️ Важно:\n"
        "Любая аналитика — это ориентир, а не гарантия.\n"
        "Рынок меняется, данные могут быть неполными.\n"
        "Финальные решения всегда остаются за тобой.\n\n"
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
# БИЗНЕС-АНАЛИЗ
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбери сценарий:",
        reply_markup=business_hub_keyboard(),
    )


async def on_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Главное меню",
        reply_markup=get_main_menu_keyboard(),
    )

# =============================
# FSM 💰 ПРИБЫЛЬ И ДЕНЬГИ (НЕ ТРОГАЛИ)
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["pm_state"] = "revenue"
    await update.message.reply_text(
        "Введи выручку:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
    )


async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("pm_state")
    text = update.message.text.replace(" ", "")

    if not text.isdigit():
        await update.message.reply_text("Введи число.")
        return

    if state == "revenue":
        context.user_data["revenue"] = int(text)
        context.user_data["pm_state"] = "expenses"
        await update.message.reply_text("Теперь расходы:")
        return

    if state == "expenses":
        revenue = context.user_data["revenue"]
        expenses = int(text)
        profit = revenue - expenses
        margin = (profit / revenue * 100) if revenue else 0
        context.user_data.clear()

        await update.message.reply_text(
            f"Прибыль: {profit}\nМаржа: {margin:.1f}%",
            reply_markup=business_hub_keyboard(),
        )

# =============================
# FSM 🚀 РОСТ И ПРОДАЖИ — FIX
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["gs_state"] = "channel"

    await update.message.reply_text(
        "Где основной канал продаж?",
        reply_markup=growth_channel_keyboard(),
    )


async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("gs_state")
    channel = update.message.text

    if state == "channel":
        context.user_data.clear()

        await update.message.reply_text(
            "🚀 План роста:\n\n"
            "1️⃣ Сфокусируйся на одном канале\n"
            "2️⃣ Проверь оффер и упаковку\n"
            "3️⃣ Получи первые 10–20 откликов\n\n"
            "Это ориентир, а не гарантия.",
            reply_markup=business_hub_keyboard(),
        )

# =============================
# FSM ROUTER
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("pm_state"):
        await pm_handler(update, context)
    elif context.user_data.get("gs_state"):
        await growth_handler(update, context)

# =============================
# ДРУГИЕ РАЗДЕЛЫ
# =============================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скоро.", reply_markup=get_main_menu_keyboard())


async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скоро.", reply_markup=get_main_menu_keyboard())


async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скоро.", reply_markup=get_main_menu_keyboard())

# =============================
# REGISTER
# =============================

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
