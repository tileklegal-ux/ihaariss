# -*- coding: utf-8 -*-

import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from handlers.user_keyboards import (
    BTN_AI_CHAT,
    BTN_EXIT_CHAT,
    ai_chat_keyboard,
)
from telegram.ext import ContextTypes, MessageHandler, filters

from handlers.user_texts import t

from handlers.user_keyboards import (
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

from handlers.user_helpers import (
    clear_fsm,
    save_insights,
    insights_bridge_text,
)

# ✅ ЕДИНСТВЕННЫЙ “владелец” личного кабинета и экспорта — handlers/profile.py
# Импорты профиля и экспорта оставлены, т.к. они вызываются из роутера
from handlers.profile import on_profile, on_export_excel, on_export_pdf

# ✅ ДОБАВЛЕНО: юридические документы
from handlers.documents import on_documents

# Клиент OpenAI
from services.openai_client import ask_openai

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

# премиум-флаг, который читает profile.py
PREMIUM_KEY = "is_premium"

# =============================
# START / ONBOARDING
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)

    if "lang" not in context.user_data:
        context.user_data["lang"] = "ru"

    user = update.effective_user
    # Исправлена логика получения имени пользователя
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
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(t(lang, "choose_section"), reply_markup=main_menu_keyboard())

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хорошо. Я рядом.", reply_markup=main_menu_keyboard())

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
    lang = context.user_data.get("lang", "ru") # Добавлено для потенциальной локализации

    await update.message.reply_text(
        bridge +
        t(lang, "pm_start_text"), # Предполагается, что текст для PM_START вынесен в user_texts
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
    )

async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_raw = (update.message.text or "")
    # Очистка и удаление пробелов/запятых
    text = text_raw.replace(" ", "").replace(",", "").strip()
    
    # Синтаксическое исправление: `isdigit()` не работает с отрицательными числами, но
    # для выручки/расходов нужны только положительные (или 0).
    if not text.isdigit() and not (text.startswith("-") and text[1:].isdigit()):
        await update.message.reply_text("Введи число, без букв и символов, кроме минуса.")
        return

    state = context.user_data.get(PM_STATE_KEY)

    if state == PM_STATE_REVENUE:
        try:
            revenue = int(text)
        except ValueError:
            await update.message.reply_text("Пожалуйста, введи корректное число для выручки.")
            return

        context.user_data["revenue"] = revenue
        context.user_data[PM_STATE_KEY] = PM_STATE_EXPENSES
        await update.message.reply_text(
            "Теперь укажи расходы за этот же месяц.\n"
            "Закупки, реклама, аренда, сервисы, комиссии.\n"
            "Если сомневаешься — лучше завысить, чем забыть.\n"
            "Нужна общая сумма."
        )
        return

    if state == PM_STATE_EXPENSES:
        try:
            expenses = int(text)
        except ValueError:
            await update.message.reply_text("Пожалуйста, введи корректное число для расходов.")
            return

        revenue = context.user_data.get("revenue", 0)
        profit = revenue - expenses
        # Исправление деления на ноль: теперь корректно обрабатывается случай revenue == 0
        margin = (profit / revenue * 100) if revenue else 0

        risk_level = "средний"
        if revenue <= 0 and profit <= 0: # Скорректировано условие для "высокого" риска при нулевой/отрицательной выручке
            risk_level = "высокий"
        else:
            if margin < 0:
                risk_level = "высокий"
            elif margin < 10:
                risk_level = "средний"
            else:
                risk_level = "низкий"

        last_verdict = "Осторожно"
        if margin >= 10:
            last_verdict = "Можно смотреть"
        if margin < 0:
            last_verdict = "Высокий риск"

        save_insights(
            context,
            last_scenario="💰 Деньги",
            last_verdict=last_verdict,
            risk_level=risk_level
        )
        clear_fsm(context) # Очистка FSM происходит после сохранения, как и должно быть

        base_text = (
            "Итог за месяц:\n"
            "Прибыль — разница между выручкой и расходами.\n"
            "Маржа показывает, сколько остаётся с каждого рубля.\n"
            "Это не оценка бизнеса, а снимок текущего состояния.\n\n"
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
            f"Данные: выручка={revenue}, расходы={expenses}, прибыль={profit}, маржа%={margin:.1f}.\n"
        )

        ai_text = await ask_openai(ai_prompt)

        await update.message.reply_text(
            base_text + "\nКороткий разбор:\n" + ai_text,
            reply_markup=business_hub_keyboard(), # Возврат в хаб, а не в главное меню
        )

# =============================
# 🚀 РОСТ И ПРОДАЖИ
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    # Присвоение значения для FSM
    context.user_data[GROWTH_KEY] = True 
    bridge = insights_bridge_text(context)

    await update.message.reply_text(
        bridge +
        "🚀 Рост и продажи\n\n"
        "Этот шаг нужен не для оценки эффективности.\n"
        "Мы просто фиксируем, откуда клиенты приходят сейчас,\n"
        "без ожиданий и планов на рост.\n\n"
        "Выбери канал, который реально приводит клиентов сегодня,\n"
        "даже если он кажется нестабильным или случайным.",
        reply_markup=growth_channels_keyboard(),
    )

async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = update.message.text or ""

    save_insights(
        context,
        last_scenario="🚀 Рост",
        last_verdict=f"Зафиксировали текущий канал: {channel}" # Добавление канала в вердикт
    )
    clear_fsm(context)

    await update.message.reply_text(
        "📈 Текущая картина:\n\n"
        f"Источник клиентов: {channel}\n\n"
        "Мы зафиксировали основной источник клиентов.\n"
        "Это не оценка и не вывод о качестве канала,\n"
        "а точка текущего состояния.\n\n"
        "Рост — это нагрузка на систему.\n"
        "Важно не ускоряться, а понимать пределы и узкие места.",
        reply_markup=business_hub_keyboard(), # Возврат в хаб
    )

# =============================
# 📦 АНАЛИТИКА ТОВАРА
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[TA_STATE_KEY] = TA_STAGE
    bridge = insights_bridge_text(context)

    await update.message.reply_text(
        bridge +
        "📦 Аналитика товара\n\n"
        "Этот сценарий не даёт ответов «стоит или нет».\n"
        "Он помогает спокойно посмотреть на ограничения\n"
        "и снизить риск самообмана.\n\n"
        "На какой стадии ты сейчас?",
        reply_markup=step_keyboard([
            "Рассматриваю конкретный товар",
            "Есть идея, без деталей",
            "Просто изучаю рынок"
        ]),
    )

async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get(TA_STATE_KEY)
    ans = update.message.text or ""

    if state == TA_STAGE:
        context.user_data["product_stage"] = ans
        context.user_data[TA_STATE_KEY] = TA_PURPOSE
        await update.message.reply_text(
            "Разберёмся, почему люди вообще его покупают.\n\n"
            "Зачем этот товар покупают чаще всего?",
            reply_markup=step_keyboard([
                "Решает конкретную проблему",
                "Удобство / улучшение",
                "Желание / эмоция",
                "Не до конца понятно"
            ]),
        )
        return

    if state == TA_PURPOSE:
        context.user_data["product_purpose"] = ans
        context.user_data[TA_STATE_KEY] = TA_SEASON
        await update.message.reply_text(
            "Теперь посмотрим, как спрос на него распределяется во времени.\n\n"
            "Как выглядит спрос во времени?",
            reply_markup=step_keyboard(["Ровный", "Волнами", "Сезонный", "Ситуативный"]),
        )
        return

    if state == TA_SEASON:
        context.user_data["seasonality"] = ans
        context.user_data[TA_STATE_KEY] = TA_COMP
        await update.message.reply_text(
            "Посмотрим, насколько много внимания за него уже борются.\n\n"
            "Как ощущается конкуренция вокруг этого товара?",
            reply_markup=step_keyboard(["Тихо", "Заметно", "Перегрето"]),
        )
        return

    if state == TA_COMP:
        context.user_data["competition"] = ans
        context.user_data[TA_STATE_KEY] = TA_PRICE
        await update.message.reply_text(
            "Оценим чувствительность к цене.\n\n"
            "Что произойдёт, если цена станет выше?",
            reply_markup=step_keyboard(["Купят", "Сравнят", "Уйдут"]),
        )
        return

    if state == TA_PRICE:
        context.user_data["price_reaction"] = ans
        context.user_data[TA_STATE_KEY] = TA_RESOURCE
        await update.message.reply_text(
            "И напоследок — сверим идею с ресурсом.\n\n"
            "Что у тебя сейчас есть для старта?",
            reply_markup=step_keyboard(["Деньги", "Время", "Экспертиза", "Минимальный ресурс"]),
        )
        return

    if state == TA_RESOURCE:
        context.user_data["resource"] = ans
        await send_ta_result(update, context)

async def send_ta_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    stage = data.get("product_stage", "")
    purpose = data.get("product_purpose", "")
    season = data.get("seasonality", "")
    comp = data.get("competition", "")
    price = data.get("price_reaction", "")
    resource = data.get("resource", "")

    # Логика определения типа спроса
    demand_type = "непонятно"
    if purpose == "Решает конкретную проблему":
        demand_type = "проблема"
    elif purpose == "Удобство / улучшение":
        demand_type = "удобство"
    elif purpose == "Желание / эмоция":
        demand_type = "желание"

    # Логика определения сезонности
    seasonality = "стабильно"
    if season in ("Сезонный", "Ситуативный"):
        seasonality = "сезонно"
    elif season == "Волнами":
        seasonality = "волнами"

    # Логика определения конкуренции
    competition = "средняя"
    if comp == "Тихо":
        competition = "низкая"
    elif comp == "Перегрето":
        competition = "высокая"

    # Логика определения уровня ресурса
    resource_level = "ограниченно"
    if resource in ("Деньги", "Время", "Экспертиза"):
        resource_level = "достаточно"
    if resource == "Минимальный ресурс":
        resource_level = "минимально"

    # Логика вердикта и риска
    verdict = "Осторожно"
    risk_level = "средний"

    if purpose == "Решает конкретную проблему" and resource != "Минимальный ресурс":
        verdict = "Гипотеза допустима для проверки, но не является рекомендацией"
        risk_level = "средний"
    if purpose in ("Желание / эмоция", "Не до конца понятно") and resource == "Минимальный ресурс":
        verdict = "Высокий риск"
        risk_level = "высокий"
    
    # Синтаксическое исправление: `resource_level` должен быть "достаточно"
    if competition == "низкая" and seasonality == "стабильно" and resource_level == "достаточно":
        risk_level = "низкий"

    # Сохранение результатов
    save_insights(
        context,
        last_scenario="📦 Товар",
        # Исправление: упрощенное условие для last_verdict
        last_verdict=verdict, 
        risk_level=risk_level,
        demand_type=demand_type,
        seasonality=seasonality,
        competition=competition,
        resource=resource_level,
    )
    clear_fsm(context)

    base_text = (
        "Мы зафиксировали текущее состояние товара.\n"
        "Вердикт — это ориентир, а не решение.\n\n"
        f"Вердикт: {verdict}\n"
    )

    ai_prompt = (
        "Дай короткий аналитический разбор по карточке товара/идеи.\n"
        "Запрещено: советы, обещания, прогнозы, директивы.\n"
        "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
        "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
        f"Стадия={stage}\n"
        f"Причина покупки={purpose}\n"
        f"Спрос по времени={season}\n"
        f"Конкуренция={comp}\n"
        f"Реакция на рост цены={price}\n"
        f"Ресурс={resource}\n"
        f"Ориентир-вердикт={verdict}\n"
    )

    ai_text = await ask_openai(ai_prompt)

    await update.message.reply_text(
        base_text + "\nКороткий разбор:\n" + ai_text,
        reply_markup=main_menu_keyboard(), # Возврат в главное меню
    )

# =============================
# 🔎 ПОДБОР НИШИ
# =============================

NS_GOAL_START = "Запуск с нуля"
NS_GOAL_SWITCH = "Поиск нового направления"
NS_GOAL_RESEARCH = "Исследую рынок"

NS_FORMAT_GOODS = "Товары"
NS_FORMAT_SERVICE = "Услуги"
NS_FORMAT_ONLINE = "Онлайн / цифровое"
NS_FORMAT_UNKNOWN = "Пока не знаю"

NS_DEMAND_PROBLEM = "Решение проблемы"
NS_DEMAND_REGULAR = "Регулярная потребность"
NS_DEMAND_EMOTION = "Интерес / желание"
NS_DEMAND_UNKNOWN = "Не понимаю"

NS_SEASON_STABLE = "Нужна стабильность"
NS_SEASON_OK = "Готов к колебаниям"
NS_SEASON_UNKNOWN = "Не задумывался"

NS_COMPETITION_HARD = "Готов к плотному рынку"
NS_COMPETITION_SOFT = "Хочу менее занятые ниши"
NS_COMPETITION_UNKNOWN = "Не знаю, как оценивать"

NS_RESOURCE_MONEY = "Деньги"
NS_RESOURCE_TIME = "Время"
NS_RESOURCE_EXPERT = "Экспертиза"
NS_RESOURCE_MIN = "Минимальный ресурс"

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[NS_STEP_KEY] = 1
    bridge = insights_bridge_text(context)

    await update.message.reply_text(
        bridge + "🔎 Подбор ниши\n\n"
        "Зачем ты сейчас смотришь ниши?",
        reply_markup=step_keyboard([NS_GOAL_START, NS_GOAL_SWITCH, NS_GOAL_RESEARCH]),
    )

async def ns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get(NS_STEP_KEY)
    ans = update.message.text or ""

    if step == 1:
        context.user_data["goal"] = ans
        context.user_data[NS_STEP_KEY] = 2
        await update.message.reply_text(
            "Какой формат тебе ближе?",
            reply_markup=step_keyboard([NS_FORMAT_GOODS, NS_FORMAT_SERVICE, NS_FORMAT_ONLINE, NS_FORMAT_UNKNOWN]),
        )
        return

    if step == 2:
        context.user_data["format"] = ans
        context.user_data[NS_STEP_KEY] = 3
        await update.message.reply_text(
            "На чём должен держаться спрос?",
            reply_markup=step_keyboard([NS_DEMAND_PROBLEM, NS_DEMAND_REGULAR, NS_DEMAND_EMOTION, NS_DEMAND_UNKNOWN]),
        )
        return

    if step == 3:
        context.user_data["demand"] = ans
        context.user_data[NS_STEP_KEY] = 4
        await update.message.reply_text(
            "Как ты относишься к сезонности?",
            reply_markup=step_keyboard([NS_SEASON_STABLE, NS_SEASON_OK, NS_SEASON_UNKNOWN]),
        )
        return

    if step == 4:
        context.user_data["seasonality"] = ans
        context.user_data[NS_STEP_KEY] = 5
        await update.message.reply_text(
            "Как ты смотришь на конкуренцию?",
            reply_markup=step_keyboard([NS_COMPETITION_HARD, NS_COMPETITION_SOFT, NS_COMPETITION_UNKNOWN]),
        )
        return

    if step == 5:
        context.user_data["competition"] = ans
        context.user_data[NS_STEP_KEY] = 6
        await update.message.reply_text(
            "Что у тебя есть на старт?",
            reply_markup=step_keyboard([NS_RESOURCE_MONEY, NS_RESOURCE_TIME, NS_RESOURCE_EXPERT, NS_RESOURCE_MIN]),
        )
        return

    if step == 6:
        context.user_data["resource"] = ans

        # Сбор данных
        goal = context.user_data.get("goal", "")
        fmt = context.user_data.get("format", "")
        demand = context.user_data.get("demand", "")
        season = context.user_data.get("seasonality", "")
        comp = context.user_data.get("competition", "")
        res = context.user_data.get("resource", "")

        verdict = "Осторожно"
        risk_level = "средний"

        # Логика вердикта и риска
        if demand == NS_DEMAND_PROBLEM and res != NS_RESOURCE_MIN:
            verdict = "Можно смотреть"
            risk_level = "средний"
        if demand == NS_DEMAND_EMOTION and res == NS_RESOURCE_MIN:
            verdict = "Высокий риск"
            risk_level = "высокий"
        
        # Установка вспомогательных флагов для insights
        demand_type = "непонятно"
        if demand == NS_DEMAND_PROBLEM:
            demand_type = "проблема"
        elif demand == NS_DEMAND_REGULAR:
            demand_type = "регулярность"
        elif demand == NS_DEMAND_EMOTION:
            demand_type = "желание"

        seasonality = "стабильно"
        if season == NS_SEASON_OK:
            seasonality = "сезонно"
        elif season == NS_SEASON_UNKNOWN:
            seasonality = "неясно"

        competition_insight = "средняя"
        if comp == NS_COMPETITION_SOFT:
            competition_insight = "низкая"
        elif comp == NS_COMPETITION_HARD:
            competition_insight = "высокий"
        elif comp == NS_COMPETITION_UNKNOWN:
            competition_insight = "неясно"

        resource_level = "ограниченно"
        if res in (NS_RESOURCE_MONEY, NS_RESOURCE_TIME, NS_RESOURCE_EXPERT):
            resource_level = "достаточно"
        if res == NS_RESOURCE_MIN:
            resource_level = "минимально"

        # Сохранение
        save_insights(
            context,
            last_scenario="🔎 Ниша",
            last_verdict=verdict,
            risk_level=risk_level,
            demand_type=demand_type,
            seasonality=seasonality,
            competition=competition_insight, # Исправлено: использование переменной competition_insight
            resource=resource_level,
        )

        clear_fsm(context)

        base_text = (
            f"Вердикт: {verdict}\n\n"
            "Вердикт — ориентир, а не рекомендация.\n"
        )

        ai_prompt = (
            "Дай короткий аналитический разбор по выбору направления (ниша).\n"
            "Запрещено: советы, обещания, прогнозы, директивы.\n"
            "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"Зачем={goal}\n"
            f"Формат={fmt}\n"
            f"Спрос={demand}\n"
            f"Сезонность={season}\n"
            f"Конкуренция={comp}\n"
            f"Ресурс={res}\n"
            f"Ориентир-вердикт={verdict}\n"
        )

        ai_text = await ask_openai(ai_prompt)

        await update.message.reply_text(
            base_text + "\nКороткий разбор:\n" + ai_text,
            reply_markup=main_menu_keyboard(),
        )

# =============================
# ❤️ PREMIUM
# =============================

async def premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)

    OFFER_URL = "https://www.notion.so/Premium-2c901cd07aa7808b85ddec9d8019e742?source=copy_link"

    # Исправлены орфографические ошибки в числах (тире заменены на обычный минус)
    text = (
        "❤️ Premium\n\n"
        "Быстро и по делу: цены + подключение.\n\n"
        "💳 Стоимость:\n"
        "1 месяц — 499 сом / 2 499 ₸ / 449 ₽\n"
        "6 месяцев — 2 699 сом / 13 499 ₸ / 2 399 ₽\n"
        "12 месяцев — 4 999 сом / 24 999 ₸ / 4 499 ₽\n\n"
        "📩 Подключение через менеджера:\n"
        "@Artbazar_marketing\n\n"
        "Оплачивая Premium-доступ, вы принимаете условия публичной оферты."
    )

    offer_kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📄 Публичная оферта (Premium)", url=OFFER_URL)]]
    )

    await update.message.reply_text(text, reply_markup=offer_kb)
    # Удален лишний пустой ответ, который просто менял клавиатуру.
    # Клавиатура Premium должна быть прикреплена к предыдущему сообщению,
    # но поскольку в оригинале она была во втором сообщении, сохраним эту структуру:
    await update.message.reply_text(
        "Выбери действие:", # Более осмысленная фраза
        reply_markup=premium_keyboard(),
    )


async def premium_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Что ты получишь в Premium\n\n"
        "1) Глубже разбор рисков\n"
        "2) История результатов\n"
        "3) Экспорт PDF / Excel\n\n"
        "Это ориентир, а не рекомендация.\n"
        "Решение остаётся за тобой.",
        # Клавиатура BTN_BACK должна возвращать в Premium Menu
        reply_markup=premium_keyboard(), 
    )

# =============================
# 💬 AI ЧАТ ФУНКЦИИ
# Вынесены, чтобы избежать конфликтов в роутере
# =============================

async def ai_chat_enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Активация режима AI-чата."""
    context.user_data["ai_chat_mode"] = True
    await update.message.reply_text(
        "🤖 AI-чат активирован.\n\n"
        "Напиши любой вопрос.\n"
        f"Чтобы выйти — нажми «{BTN_EXIT_CHAT}».",
        reply_markup=ai_chat_keyboard(),
    )

async def ai_chat_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выход из режима AI-чата."""
    context.user_data.pop("ai_chat_mode", None)
    await update.message.reply_text(
        "Ты вышел из AI-чата.",
        reply_markup=main_menu_keyboard(),
    )

async def ai_chat_handler_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений внутри режима AI-чата (FSM-независимый)."""
    text = update.message.text or ""

    # Выход из AI-чата (если пришла кнопка)
    if text in (BTN_BACK, BTN_EXIT_CHAT):
        # В этом режиме кнопка должна быть обработана как выход
        await ai_chat_exit(update, context)
        return

    user_text = text.strip()

    if not user_text:
        return

    # Защита: команды не пускаем
    if user_text.startswith("/"):
        await update.message.reply_text(
             "Пожалуйста, введи вопрос текстом. Команды в этом режиме игнорируются."
        )
        return
    
    # Запрос к AI
    # Импорт тут не нужен, так как он уже есть в начале файла
    # from services.openai_client import ask_ai_chat 

    await update.message.chat.send_action("typing")

    try:
        
        ai_prompt = (
            "Ты — AI-ассистент Essence Dev.\n"
            "Ты помогаешь предпринимателям спокойно анализировать идеи, но не даешь советов и прогнозов.\n"
            "Формат: 1) Наблюдения, 2) Риски, 3) Варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"Текст пользователя:\n{user_text}"
        )

        answer = await ask_openai(ai_prompt)

        await update.message.reply_text(answer, reply_markup=ai_chat_keyboard())

    except Exception as e:
        logger.error(f"AI Chat Error: {e}")
        await update.message.reply_text(
            "⚠️ Не удалось получить ответ от AI. Попробуй ещё раз.",
            reply_markup=ai_chat_keyboard(),
        )
    
    return # Выход из роутера после обработки сообщения в AI-чате

# =============================
# ROUTER (ЕДИНЫЙ И СТРУКТУРИРОВАННЫЙ)
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    
    # ------------------------------------
    # 0. СБРОС AI CHAT MODE (ОБРАБОТКА КНОПОК)
    # ------------------------------------
    # При нажатии на любую кнопку главного меню или FSM-сценария,
    # мы сбрасываем флаг AI-чата, чтобы не сработала AI-логика.
    
    is_fsm_or_main_menu_button = text in (
        BTN_BIZ, BTN_PM, BTN_GROWTH, BTN_ANALYSIS, BTN_NICHE, 
        BTN_PROFILE, BTN_PREMIUM, BTN_PREMIUM_BENEFITS, BTN_AI_CHAT, "📊 Скачать Excel", "📄 Скачать PDF", "📄 Документы", "📄 Документы и условия", "ℹ️ О нас", "ℹ️ О проекте"
    )

    if context.user_data.get("ai_chat_mode") and (is_fsm_or_main_menu_button or text == BTN_BACK or text == BTN_EXIT_CHAT):
        # Выход из режима AI-чата, если нажата любая другая кнопка
        await ai_chat_exit(update, context)
        # После выхода из чата, роутер продолжает работу, чтобы обработать нажатую кнопку.
    elif not is_fsm_or_main_menu_button:
        # Сброс флага, если он вдруг остался без причины
        context.user_data.pop("ai_chat_mode", None)

    # ------------------------------------
    # 1. AI CHAT MODE (ПРИОРИТЕТ)
    # ------------------------------------
    if context.user_data.get("ai_chat_mode"):
        # Если сообщение пришло в режиме AI-чата, передаем его специальному обработчику
        # Обработчик ai_chat_handler_mode сам решает, как обрабатывать BTN_EXIT_CHAT/BTN_BACK
        # но мы это уже сделали выше в блоке 0, поэтому тут только текстовый ввод.
        
        # Если мы вышли из чата в блоке 0 (например, нажав BTN_BACK), то ai_chat_mode уже False.
        # Если же это чистый текстовый ввод, то ai_chat_mode True.
        
        if text not in (BTN_BACK, BTN_EXIT_CHAT):
             # Это обычный текстовый ввод, обрабатываем его как чат
             await ai_chat_handler_mode(update, context)
             return # Выход, чтобы не сработала FSM-логика на введенный текст

    # ------------------------------------
    # 2. FSM (ПРИОРИТЕТ)
    # ------------------------------------
    # Обработка кнопки "Назад" внутри FSM
    if text == BTN_BACK:
        if context.user_data.get(PM_STATE_KEY) or context.user_data.get(GROWTH_KEY) or context.user_data.get(TA_STATE_KEY):
            clear_fsm(context)
            await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
            return
        if context.user_data.get(NS_STEP_KEY):
            clear_fsm(context)
            await update.message.reply_text("Главное меню", reply_markup=main_menu_keyboard())
            return
        
        # Общий BACK
        await update.message.reply_text("Главное меню", reply_markup=main_menu_keyboard())
        return

    # Обработка FSM-ввода
    if context.user_data.get(PM_STATE_KEY):
        await pm_handler(update, context)
        return
    
    if context.user_data.get(GROWTH_KEY):
        await growth_handler(update, context)
        return
    
    if context.user_data.get(TA_STATE_KEY):
        await ta_handler(update, context)
        return
    
    if context.user_data.get(NS_STEP_KEY):
        await ns_handler(update, context)
        return

    # ------------------------------------
    # 3. СПЕЦИАЛЬНЫЕ КОМАНДЫ И КНОПКИ (NON-FSM)
    # ------------------------------------
    
    # Онбординг (YES/NO)
    if text == BTN_YES:
        await on_yes(update, context)
        return
    if text == BTN_NO:
        await on_no(update, context)
        return

    # Главное меню (вход в FSM-сценарии или разделы)
    if text == BTN_BIZ:
        await on_business_analysis(update, context)
        return
    if text == BTN_PM:
        await pm_start(update, context)
        return
    if text == BTN_GROWTH:
        await growth_start(update, context)
        return
    if text == BTN_ANALYSIS:
        await ta_start(update, context)
        return
    if text == BTN_NICHE:
        await ns_start(update, context)
        return
    if text == BTN_PROFILE:
        await on_profile(update, context)
        return
    if text == BTN_PREMIUM:
        await premium_start(update, context)
        return
    
    # Вход в AI-чат
    if text == BTN_AI_CHAT:
        # Уже обработано в блоке 0, но на всякий случай, если код дойдет досюда
        await ai_chat_enter(update, context)
        return
        
    # Премиум-меню
    if text == BTN_PREMIUM_BENEFITS:
        await premium_benefits(update, context)
        return
    
    # Экспорт (Premium кабинет)
    if text == "📊 Скачать Excel":
        await on_export_excel(update, context)
        return
    if text == "📄 Скачать PDF":
        await on_export_pdf(update, context)
        return

    # ✅ ДОБАВЛЕНО: Документы и условия
    if text in ("📄 Документы", "📄 Документы и условия", "ℹ️ О нас", "ℹ️ О проекте"):
        await on_documents(update, context)
        return

    # ------------------------------------
    # 4. ФОЛЛБЕК
    # ------------------------------------
    # ⚠️ ЭТОТ БЛОК ДОЛЖЕН БЫТЬ ВНУТРИ ASYNC DEF text_router
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(t(lang, "choose_section"), reply_markup=main_menu_keyboard())

# =============================
# REGISTER
# =============================

def register_handlers_user(app):
    # Добавление обработчика для команды /start
    from telegram.ext import CommandHandler
    app.add_handler(CommandHandler("start", cmd_start_user))
    
    # Добавление основного обработчика текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    
    # Обработчики для других типов сообщений (необязательно, но для полноты)
    # app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.LOCATION, some_fallback_handler))
