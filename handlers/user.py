from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

# ==================================================
# КНОПКИ ОСНОВНЫЕ
# ==================================================

BTN_YES = "Да"
BTN_NO = "Нет"

BTN_BIZ = "📊 Бизнес-анализ"
BTN_ANALYSIS = "📦 Аналитика товара"
BTN_NICHE = "🔎 Подбор ниши"
BTN_PROFILE = "👤 Личный кабинет"
BTN_PREMIUM = "❤️ Premium"
BTN_BACK = "⬅️ Назад"
BTN_MENU = "◀️ В меню"

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


def step_keyboard(buttons):
    rows = [[KeyboardButton(b)] for b in buttons]
    rows.append([KeyboardButton(BTN_MENU)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

# ==================================================
# START
# ==================================================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    name = user.first_name or "друг"

    await update.message.reply_text(
        f"Привет, {name} 👋\n\n"
        "Ты в Artbazar AI — аналитическом помощнике.\n\n"
        "Я помогаю:\n"
        "• разложить бизнес-решения по полочкам\n"
        "• снизить неопределённость\n"
        "• избежать лишних ошибок\n\n"
        "⚠️ Это не прогноз и не совет.\n"
        "Решение всегда остаётся за тобой.\n\n"
        "Продолжим?",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )

async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери раздел 👇", reply_markup=main_menu_keyboard())

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хорошо. Я рядом.", reply_markup=main_menu_keyboard())

# ==================================================
# 🔎 ПОДБОР НИШИ — FSM v1
# ==================================================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["ns_step"] = 1

    await update.message.reply_text(
        "🔎 Подбор ниши\n\n"
        "Здесь мы не ищем «лучшую нишу».\n"
        "Мы фиксируем рамки и уровень риска.\n\n"
        "Зачем ты сейчас смотришь ниши?",
        reply_markup=step_keyboard(
            ["Запуск с нуля", "Смена направления", "Изучаю рынок"]
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
            reply_markup=step_keyboard(
                ["Товары", "Услуги", "Онлайн / цифровое", "Пока не знаю"]
            ),
        )
        return

    if step == 2:
        context.user_data["format"] = text
        context.user_data["ns_step"] = 3
        await update.message.reply_text(
            "На чём должен держаться спрос?",
            reply_markup=step_keyboard(
                ["Решение проблемы", "Регулярная потребность", "Интерес / эмоция", "Не уверен"]
            ),
        )
        return

    if step == 3:
        context.user_data["demand"] = text
        context.user_data["ns_step"] = 4
        await update.message.reply_text(
            "Как ты относишься к сезонности?",
            reply_markup=step_keyboard(
                ["Нужна стабильность", "Готов к колебаниям", "Не думал"]
            ),
        )
        return

    if step == 4:
        context.user_data["season"] = text
        context.user_data["ns_step"] = 5
        await update.message.reply_text(
            "Как ты воспринимаешь конкуренцию?",
            reply_markup=step_keyboard(
                ["Готов к плотному рынку", "Хочу спокойнее", "Не знаю"]
            ),
        )
        return

    if step == 5:
        context.user_data["competition"] = text
        context.user_data.clear()

        await update.message.reply_text(
            "🎯 Итог по нише\n\n"
            "Это не рекомендация и не выбор за тебя.\n"
            "Это ориентир, который показывает рамки и риски.\n\n"
            "Осторожность здесь — не минус,\n"
            "а способ не потерять время и деньги.",
            reply_markup=main_menu_keyboard(),
        )

# ==================================================
# 📦 АНАЛИТИКА ТОВАРА — FSM v1
# ==================================================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["ta_step"] = 1

    await update.message.reply_text(
        "📦 Аналитика товара\n\n"
        "Этот сценарий не говорит «брать или нет».\n"
        "Он помогает увидеть ограничения и риски.\n\n"
        "На какой стадии ты сейчас?",
        reply_markup=step_keyboard(
            ["Конкретный товар", "Есть идея", "Просто изучаю рынок"]
        ),
    )

async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("ta_step")
    text = update.message.text

    if step == 1:
        context.user_data["stage"] = text
        context.user_data["ta_step"] = 2
        await update.message.reply_text(
            "Зачем его покупают?",
            reply_markup=step_keyboard(
                ["Решает проблему", "Удобство", "Эмоция", "Не понимаю"]
            ),
        )
        return

    if step == 2:
        context.user_data["purpose"] = text
        context.user_data["ta_step"] = 3
        await update.message.reply_text(
            "Как выглядит спрос во времени?",
            reply_markup=step_keyboard(
                ["Постоянный", "Сезонный", "Всплесками", "Не знаю"]
            ),
        )
        return

    if step == 3:
        context.user_data["season"] = text
        context.user_data["ta_step"] = 4
        await update.message.reply_text(
            "Как ощущается конкуренция?",
            reply_markup=step_keyboard(
                ["Слабо", "Заметно", "Перегрето", "Не смотрел"]
            ),
        )
        return

    if step == 4:
        context.user_data["competition"] = text
        context.user_data["ta_step"] = 5
        await update.message.reply_text(
            "Как ты планируешь цену?",
            reply_markup=step_keyboard(
                ["Ниже рынка", "Как у других", "Выше рынка", "Не думал"]
            ),
        )
        return

    if step == 5:
        context.user_data["price"] = text
        context.user_data.clear()

        await update.message.reply_text(
            "📊 Итог анализа товара\n\n"
            "Вердикт — ориентир, а не рекомендация.\n"
            "Он показывает, где решение может быть хрупким.\n\n"
            "Следующий шаг — аккуратный тест или уточнение гипотезы.\n"
            "Ответственность за решение остаётся за тобой.",
            reply_markup=main_menu_keyboard(),
        )

# ==================================================
# ПРОЧЕЕ
# ==================================================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Личный кабинет\n\nИстория появится позже.",
        reply_markup=main_menu_keyboard(),
    )

async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ Premium\n\n"
        "Помогает глубже разобраться в рисках.\n"
        "Без советов и без обещаний.\n\n"
        "📩 @Artbazar_marketing",
        reply_markup=main_menu_keyboard(),
    )

# ==================================================
# ROUTER
# ==================================================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("ns_step"):
        await ns_handler(update, context)
    elif context.user_data.get("ta_step"):
        await ta_handler(update, context)

# ==================================================
# REGISTER
# ==================================================

def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NICHE}$"), ns_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), on_premium))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_MENU}$"), cmd_start_user))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
