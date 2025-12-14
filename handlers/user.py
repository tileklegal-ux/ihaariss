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

BTN_ANALYSIS = "📦 Аналитика товара"
BTN_NICHE = "🔎 Подбор ниши"
BTN_PROFILE = "👤 Личный кабинет"
BTN_PREMIUM = "❤️ Premium"

# =============================
# КНОПКИ ПОДБОРА НИШИ
# =============================

NS_GOAL_START = "🚀 Запуск бизнеса"
NS_GOAL_SWITCH = "🔄 Смена направления"
NS_GOAL_RESEARCH = "👀 Изучаю рынок"

NS_FORMAT_GOODS = "📦 Товары"
NS_FORMAT_SERVICE = "🛠 Услуги"
NS_FORMAT_ONLINE = "🌐 Онлайн / цифровое"
NS_FORMAT_UNKNOWN = "❓ Пока не знаю"

NS_DEMAND_PROBLEM = "🩹 Решение проблемы"
NS_DEMAND_REGULAR = "🔁 Регулярная потребность"
NS_DEMAND_EMOTION = "🎯 Интерес / эмоция"
NS_DEMAND_UNKNOWN = "❓ Не уверен"

NS_SEASON_STABLE = "📈 Нужна стабильность"
NS_SEASON_OK = "🌊 Готов к сезонности"
NS_SEASON_UNKNOWN = "❓ Не думал"

NS_COMPETITION_HARD = "⚔️ Готов к конкуренции"
NS_COMPETITION_SOFT = "🟢 Хочу спокойнее"
NS_COMPETITION_UNKNOWN = "❓ Не знаю"

NS_RESOURCE_MONEY = "💰 Деньги"
NS_RESOURCE_TIME = "⏱ Время"
NS_RESOURCE_EXPERT = "🧠 Экспертиза"
NS_RESOURCE_MIN = "⚠️ Минимум ресурса"

# =============================
# КЛАВИАТУРЫ
# =============================

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

def niche_step_keyboard(buttons):
    rows = [[KeyboardButton(b)] for b in buttons]
    rows.append([KeyboardButton(BTN_BACK)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

# =============================
# START
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    name = user.first_name or user.username or "друг"

    await update.message.reply_text(
        f"Привет, {name} 👋\n\n"
        "Ты в Artbazar AI — аналитическом помощнике для предпринимателей.\n\n"
        "Я помогаю:\n"
        "• разложить решения по полочкам\n"
        "• снизить неопределённость\n"
        "• избежать лишних ошибок\n\n"
        "⚠️ Важно:\n"
        "Это не прогноз и не гарантия.\n"
        "Решения всегда остаются за тобой.\n\n"
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

# =============================
# БИЗНЕС-АНАЛИЗ
# =============================

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

# =============================
# 🔎 ПОДБОР НИШИ — FSM v1
# =============================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["ns_step"] = 1

    await update.message.reply_text(
        "🔎 Подбор ниши\n\n"
        "Здесь мы не ищем «лучшую нишу».\n"
        "Мы фиксируем рамки и уровень риска,\n"
        "с которыми тебе будет комфортно работать.\n\n"
        "Зачем ты сейчас смотришь ниши?",
        reply_markup=niche_step_keyboard(
            [NS_GOAL_START, NS_GOAL_SWITCH, NS_GOAL_RESEARCH]
        ),
    )

async def ns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("ns_step")
    text = update.message.text

    if step == 1:
        context.user_data["goal"] = text
        context.user_data["ns_step"] = 2
        await update.message.reply_text(
            "Какой формат тебе ближе?",
            reply_markup=niche_step_keyboard(
                [NS_FORMAT_GOODS, NS_FORMAT_SERVICE, NS_FORMAT_ONLINE, NS_FORMAT_UNKNOWN]
            ),
        )
        return

    if step == 2:
        context.user_data["format"] = text
        context.user_data["ns_step"] = 3
        await update.message.reply_text(
            "На чём должен строиться спрос?",
            reply_markup=niche_step_keyboard(
                [NS_DEMAND_PROBLEM, NS_DEMAND_REGULAR, NS_DEMAND_EMOTION, NS_DEMAND_UNKNOWN]
            ),
        )
        return

    if step == 3:
        context.user_data["demand"] = text
        context.user_data["ns_step"] = 4
        await update.message.reply_text(
            "Как ты относишься к сезонности?",
            reply_markup=niche_step_keyboard(
                [NS_SEASON_STABLE, NS_SEASON_OK, NS_SEASON_UNKNOWN]
            ),
        )
        return

    if step == 4:
        context.user_data["season"] = text
        context.user_data["ns_step"] = 5
        await update.message.reply_text(
            "Как ты воспринимаешь конкуренцию?",
            reply_markup=niche_step_keyboard(
                [NS_COMPETITION_HARD, NS_COMPETITION_SOFT, NS_COMPETITION_UNKNOWN]
            ),
        )
        return

    if step == 5:
        context.user_data["competition"] = text
        context.user_data["ns_step"] = 6
        await update.message.reply_text(
            "Что у тебя сейчас есть для старта?",
            reply_markup=niche_step_keyboard(
                [NS_RESOURCE_MONEY, NS_RESOURCE_TIME, NS_RESOURCE_EXPERT, NS_RESOURCE_MIN]
            ),
        )
        return

    if step == 6:
        context.user_data["resource"] = text
        context.user_data.clear()

        await update.message.reply_text(
            "🎯 Итог по подбору ниши\n\n"
            "Это не рекомендация и не выбор за тебя.\n"
            "Это ориентир, который показывает:\n"
            "— где ожидания могут не совпасть с реальностью\n"
            "— где риск выше, чем кажется\n\n"
            "Осторожность здесь — не минус,\n"
            "а способ не потерять время и деньги.\n\n"
            "Следующий шаг —\n"
            "разобрать конкретный товар или идею.",
            reply_markup=main_menu_keyboard(),
        )

# =============================
# ПРОЧЕЕ
# =============================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Личный кабинет\n\nИстория появится позже.",
        reply_markup=main_menu_keyboard(),
    )

async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ Premium\n\n"
        "Персональная помощь и расширенные сценарии.\n\n"
        "📩 Напиши: @Artbazar_marketing",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# ROUTER
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("ns_step"):
        await ns_handler(update, context)

# =============================
# REGISTER
# =============================

def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NICHE}$"), ns_start))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), on_premium))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), on_back))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
