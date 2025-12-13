from __future__ import annotations

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

import os

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

# Рост и продажи — каналы (аккуратные, читабельные)
BTN_INST = "📸 Instagram"
BTN_TG = "💬 Telegram"
BTN_MP = "🛒 Маркетплейсы"
BTN_KASPI = "🏦 Kaspi"
BTN_WB = "📦 Wildberries"
BTN_OZON = "🚚 Ozon"
BTN_OFFLINE = "🏪 Офлайн"
BTN_OTHER = "❓ Другое"

# Аналитика товара — категории (кнопки)
TA_CAT_FASHION = "👗 Одежда/аксессуары"
TA_CAT_BEAUTY = "💄 Красота"
TA_CAT_HOME = "🏠 Дом/хозтовары"
TA_CAT_KIDS = "🧸 Дети"
TA_CAT_ELECTRO = "🔌 Электроника"
TA_CAT_FOOD = "🍫 Еда"
TA_CAT_OTHER = "📦 Другое"

# Подбор ниши — сценарии (кнопки)
NS_GOAL_FAST = "⚡ Быстро заработать"
NS_GOAL_STABLE = "🧱 Стабильно и надолго"
NS_GOAL_ONLINE = "🌐 Онлайн"
NS_GOAL_OFFLINE = "🏪 Офлайн"

NS_STOCK_NO = "📦 Без склада"
NS_STOCK_YES = "🏬 Со складом"

NS_BUDGET_LOW = "💸 До $200"
NS_BUDGET_MID = "💰 $200–$1000"
NS_BUDGET_HIGH = "🏦 $1000+"

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


def back_only_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True)


def growth_channels_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_INST), KeyboardButton(BTN_TG)],
            [KeyboardButton(BTN_MP), KeyboardButton(BTN_KASPI)],
            [KeyboardButton(BTN_WB), KeyboardButton(BTN_OZON)],
            [KeyboardButton(BTN_OFFLINE), KeyboardButton(BTN_OTHER)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def ta_category_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(TA_CAT_FASHION), KeyboardButton(TA_CAT_BEAUTY)],
            [KeyboardButton(TA_CAT_HOME), KeyboardButton(TA_CAT_KIDS)],
            [KeyboardButton(TA_CAT_ELECTRO), KeyboardButton(TA_CAT_FOOD)],
            [KeyboardButton(TA_CAT_OTHER)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def ns_goal_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(NS_GOAL_FAST), KeyboardButton(NS_GOAL_STABLE)],
            [KeyboardButton(NS_GOAL_ONLINE), KeyboardButton(NS_GOAL_OFFLINE)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def ns_stock_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(NS_STOCK_NO), KeyboardButton(NS_STOCK_YES)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def ns_budget_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(NS_BUDGET_LOW), KeyboardButton(NS_BUDGET_MID)],
            [KeyboardButton(NS_BUDGET_HIGH)],
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
        "Тебя приветствует Artbazar AI — аналитический помощник для предпринимателей.\n\n"
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
    await update.message.reply_text("Выбери раздел 👇", reply_markup=main_menu_keyboard())


async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хорошо. Я рядом.", reply_markup=main_menu_keyboard())


# =============================
# 📊 БИЗНЕС-АНАЛИЗ (ХАБ)
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Бизнес-анализ\n\n"
        "Здесь быстрые расчёты и подсказки.\n"
        "Выбери сценарий:",
        reply_markup=business_hub_keyboard(),
    )


async def on_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Главное меню", reply_markup=main_menu_keyboard())


# =============================
# FSM 💰 ПРИБЫЛЬ И ДЕНЬГИ
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["pm_state"] = "revenue"

    await update.message.reply_text(
        "💰 Прибыль и деньги\n\n"
        "Коротко: считаем прибыль за месяц.\n"
        "Сейчас нужно 2 числа.\n\n"
        "1/2 — Введи *выручку в месяц* (например: 250000):",
        parse_mode="Markdown",
        reply_markup=back_only_keyboard(),
    )


async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("pm_state")
    text = update.message.text.replace(" ", "").replace(",", "")

    if state not in ("revenue", "expenses"):
        return

    if not text.isdigit():
        await update.message.reply_text("Введи число (без букв). Например: 250000")
        return

    if state == "revenue":
        context.user_data["revenue"] = int(text)
        context.user_data["pm_state"] = "expenses"

        await update.message.reply_text(
            "2/2 — Теперь введи *расходы в месяц* (например: 170000):",
            parse_mode="Markdown",
        )
        return

    if state == "expenses":
        revenue = int(context.user_data.get("revenue", 0))
        expenses = int(text)

        profit = revenue - expenses
        margin = (profit / revenue * 100) if revenue else 0

        context.user_data["last_pm"] = {
            "revenue": revenue,
            "expenses": expenses,
            "profit": profit,
            "margin": float(f"{margin:.1f}"),
        }
        context.user_data.pop("pm_state", None)

        await update.message.reply_text(
            "📊 *Результат расчёта:*\n\n"
            f"Выручка: {revenue}\n"
            f"Расходы: {expenses}\n"
            f"Прибыль: {profit}\n"
            f"Маржа: {margin:.1f}%\n\n"
            "Следующий шаг: если прибыль маленькая — проверь расходы и цену. "
            "Если прибыль нормальная — думай про рост продаж.",
            parse_mode="Markdown",
            reply_markup=business_hub_keyboard(),
        )


# =============================
# FSM 🚀 РОСТ И ПРОДАЖИ
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["gs_state"] = "channel"

    await update.message.reply_text(
        "🚀 Рост и продажи\n\n"
        "Коротко: выберем канал — и я дам 3 шага, с чего начать.\n\n"
        "Выбери основной канал продаж:",
        reply_markup=growth_channels_keyboard(),
    )


async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("gs_state") != "channel":
        return

    channel = update.message.text
    context.user_data["last_growth"] = {"channel": channel}
    context.user_data.pop("gs_state", None)

    await update.message.reply_text(
        "📈 *План роста (3 шага):*\n\n"
        f"Канал: {channel}\n\n"
        "1️⃣ Усиль поток клиентов (больше входящих)\n"
        "2️⃣ Проверь оффер (почему должны купить именно у тебя)\n"
        "3️⃣ Убери узкие места (цена, доставка, доверие, ответы)\n\n"
        "Следующий шаг: выбери один пункт и сделай сегодня 1 действие.",
        parse_mode="Markdown",
        reply_markup=business_hub_keyboard(),
    )


# =============================
# FSM 📊 АНАЛИТИКА ТОВАРА (НЕ ЗАГЛУШКА)
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["ta_state"] = "name"

    await update.message.reply_text(
        "📊 Аналитика товара\n\n"
        "Коротко: поймём, стоит ли тестировать товар.\n"
        "Нужны 4 шага.\n\n"
        "1/4 — Напиши название товара (например: «набор для ухода за обувью»):",
        reply_markup=back_only_keyboard(),
    )


async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("ta_state")
    msg = (update.message.text or "").strip()

    if state == "name":
        if len(msg) < 3:
            await update.message.reply_text("Слишком коротко. Напиши 3+ символа.")
            return
        context.user_data["ta_name"] = msg
        context.user_data["ta_state"] = "category"

        await update.message.reply_text(
            "2/4 — Выбери категорию товара:",
            reply_markup=ta_category_keyboard(),
        )
        return

    if state == "category":
        context.user_data["ta_category"] = msg
        context.user_data["ta_state"] = "price"

        await update.message.reply_text(
            "3/4 — Введи *цену продажи* (число, например 1990):",
            parse_mode="Markdown",
            reply_markup=back_only_keyboard(),
        )
        return

    if state == "price":
        text = msg.replace(" ", "").replace(",", "")
        if not text.isdigit():
            await update.message.reply_text("Введи число. Например: 1990")
            return
        context.user_data["ta_price"] = int(text)
        context.user_data["ta_state"] = "cost"

        await update.message.reply_text(
            "4/4 — Введи *себестоимость* (закуп + доставка), число:",
            parse_mode="Markdown",
        )
        return

    if state == "cost":
        text = msg.replace(" ", "").replace(",", "")
        if not text.isdigit():
            await update.message.reply_text("Введи число. Например: 1200")
            return

        name = context.user_data.get("ta_name", "")
        cat = context.user_data.get("ta_category", "")
        price = int(context.user_data.get("ta_price", 0))
        cost = int(text)

        profit = price - cost
        margin = (profit / price * 100) if price else 0

        lite_note = ""
        if not os.getenv("OPENAI_API_KEY"):
            lite_note = (
                "\n\nℹ️ Сейчас работает Lite-режим (без AI-рекомендаций). "
                "Это нормально: бот не падает и даёт базовую аналитику."
            )

        context.user_data["last_ta"] = {
            "name": name,
            "category": cat,
            "price": price,
            "cost": cost,
            "profit": profit,
            "margin": float(f"{margin:.1f}"),
        }
        context.user_data.pop("ta_state", None)

        await update.message.reply_text(
            "✅ *Краткий разбор товара:*\n\n"
            f"Товар: {name}\n"
            f"Категория: {cat}\n"
            f"Цена: {price}\n"
            f"Себестоимость: {cost}\n"
            f"Профит с единицы: {profit}\n"
            f"Маржа: {margin:.1f}%\n\n"
            "Следующий шаг:\n"
            "• если маржа < 25% — ищи дешевле закуп / подними цену / добавь комплект\n"
            "• если маржа 25–45% — можно тестировать маленькой партией\n"
            "• если маржа > 45% — тестируй и думай про канал продаж",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
        if lite_note:
            await update.message.reply_text(lite_note, reply_markup=main_menu_keyboard())


# =============================
# FSM 🔎 ПОДБОР НИШИ (НЕ ЗАГЛУШКА)
# =============================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["ns_state"] = "goal"

    await update.message.reply_text(
        "🔎 Подбор ниши\n\n"
        "Коротко: подберём 3 направления под твои условия.\n"
        "Нужно 3 шага.\n\n"
        "1/3 — Какая цель ближе?",
        reply_markup=ns_goal_keyboard(),
    )


async def ns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("ns_state")
    msg = (update.message.text or "").strip()

    if state == "goal":
        context.user_data["ns_goal"] = msg
        context.user_data["ns_state"] = "stock"
        await update.message.reply_text("2/3 — Как со складом?", reply_markup=ns_stock_keyboard())
        return

    if state == "stock":
        context.user_data["ns_stock"] = msg
        context.user_data["ns_state"] = "budget"
        await update.message.reply_text("3/3 — Какой бюджет на старт?", reply_markup=ns_budget_keyboard())
        return

    if state == "budget":
        goal = context.user_data.get("ns_goal", "")
        stock = context.user_data.get("ns_stock", "")
        budget = msg

        # Базовая логика (без “магии” и без обещаний прибыли)
        rec = []
        if NS_STOCK_NO in stock:
            rec.append("Услуги/цифровые продукты вокруг твоих навыков (без закупа и склада)")
            rec.append("Товары с быстрым оборотом и маленьким объёмом (аксессуары, расходники)")
            rec.append("Партнёрка/дроп: тест спроса без заморозки денег")
        else:
            rec.append("Ниша с повторными покупками (расходники/уход/дом)")
            rec.append("Комплектование (наборы) — легче поднять чек и маржу")
            rec.append("Локальный офлайн-хит + онлайн-витрина (гибрид)")

        lite_note = ""
        if not os.getenv("OPENAI_API_KEY"):
            lite_note = (
                "\n\nℹ️ Lite-режим: рекомендации базовые. "
                "AI-расширение подключим через ключ, бот при этом не ломается."
            )

        context.user_data["last_ns"] = {"goal": goal, "stock": stock, "budget": budget, "rec": rec}
        context.user_data.pop("ns_state", None)

        await update.message.reply_text(
            "✅ *Подбор ниши — результат:*\n\n"
            f"Цель: {goal}\n"
            f"Склад: {stock}\n"
            f"Бюджет: {budget}\n\n"
            "3 направления, с которых можно начать:\n"
            f"1) {rec[0]}\n"
            f"2) {rec[1]}\n"
            f"3) {rec[2]}\n\n"
            "Следующий шаг: выбери 1 направление — и зайди в «📊 Аналитику товара», чтобы проверить конкретный товар/оффер.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
        if lite_note:
            await update.message.reply_text(lite_note, reply_markup=main_menu_keyboard())


# =============================
# 👤 ЛИЧНЫЙ КАБИНЕТ (НЕ ЗАГЛУШКА)
# =============================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_pm = context.user_data.get("last_pm")
    last_growth = context.user_data.get("last_growth")
    last_ta = context.user_data.get("last_ta")
    last_ns = context.user_data.get("last_ns")

    lines = ["👤 Личный кабинет\n", "Тут твои последние результаты (на этом устройстве):\n"]

    if last_pm:
        lines.append(
            f"💰 Прибыль: выручка {last_pm['revenue']}, расходы {last_pm['expenses']}, "
            f"прибыль {last_pm['profit']}, маржа {last_pm['margin']}%"
        )
    else:
        lines.append("💰 Прибыль: пока нет расчёта")

    if last_growth:
        lines.append(f"🚀 Рост: канал {last_growth['channel']}")
    else:
        lines.append("🚀 Рост: пока нет")

    if last_ta:
        lines.append(
            f"📊 Товар: {last_ta['name']} | маржа {last_ta['margin']}% | профит {last_ta['profit']}"
        )
    else:
        lines.append("📊 Товар: пока нет анализа")

    if last_ns:
        lines.append(f"🔎 Ниша: {last_ns['goal']} | {last_ns['stock']} | {last_ns['budget']}")
    else:
        lines.append("🔎 Ниша: пока нет подбора")

    await update.message.reply_text("\n".join(lines), reply_markup=main_menu_keyboard())


# =============================
# ❤️ PREMIUM (НЕ ЗАГЛУШКА)
# =============================

async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ Premium\n\n"
        "Premium — это когда бот даёт *больше конкретики* и экономит тебе время:\n"
        "• расширенные рекомендации (AI)\n"
        "• более точные вопросы и выводы\n"
        "• шаблоны оффера/проверки спроса\n\n"
        "Сейчас Premium активируется через менеджера (внутри проекта).\n"
        "Если тебе нужно подключение — напиши менеджеру/админу.",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


# =============================
# ROUTER (ЕДИНЫЙ)
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Назад — всегда приоритет
    if update.message and update.message.text == BTN_BACK:
        await on_back(update, context)
        return

    # FSM по состояниям
    if context.user_data.get("pm_state"):
        await pm_handler(update, context)
        return

    if context.user_data.get("gs_state"):
        await growth_handler(update, context)
        return

    if context.user_data.get("ta_state"):
        await ta_handler(update, context)
        return

    if context.user_data.get("ns_state"):
        await ns_handler(update, context)
        return


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

    # Текстовый роутер — последним
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
