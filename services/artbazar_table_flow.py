from typing import Dict, Any, Optional

from telegram import Update
from telegram.ext import ContextTypes

try:
    # Планируемая интеграция с отдельными сервисами
    from services.ai_analysis import analyze_artbazar_table
except ImportError:
    analyze_artbazar_table = None  # fallback, если модуль ещё не создан


# Ключи в user_data
SESSION_KEY = "artbazar_table_session"


# Описание полей таблицы и их порядок
FIELDS = [
    {
        "key": "niche",
        "label": "Ниша",
        "question": "В какой нише ты планируешь работать? (например: детская одежда, электроника, косметика)",
        "type": "text",
    },
    {
        "key": "product",
        "label": "Товар",
        "question": "Какой товар собираешься продавать? (например: детский комбинезон, наушники, крем для лица)",
        "type": "text",
    },
    {
        "key": "purchase_price",
        "label": "Закупочная цена",
        "question": "Укажи закупочную цену за единицу товара (в сомах или тенге).",
        "type": "float",
    },
    {
        "key": "sale_price",
        "label": "Цена продажи",
        "question": "По какой цене планируешь продавать одну единицу товара?",
        "type": "float",
    },
    {
        "key": "platform_commission_percent",
        "label": "Комиссия площадки (%)",
        "question": "Комиссия маркетплейса или платформы в процентах (%). Если нет комиссии — напиши 0.",
        "type": "float",
    },
    {
        "key": "logistics",
        "label": "Логистика",
        "question": "Сколько стоит логистика (склад, доставка до склада, таможня и т.п.) на одну единицу товара?",
        "type": "float",
    },
    {
        "key": "delivery",
        "label": "Доставка",
        "question": "Сколько стоит доставка до клиента на одну единицу товара?",
        "type": "float",
    },
    {
        "key": "marketing",
        "label": "Маркетинг",
        "question": "Бюджет маркетинга на одну продажу (контекст, таргет, блогеры и т.д.)?",
        "type": "float",
    },
    {
        "key": "other_expenses",
        "label": "Прочие расходы",
        "question": "Какие ещё есть расходы на одну единицу товара? (например: упаковка, возвраты, налоги). Укажи суммой.",
        "type": "float",
    },
    {
        "key": "risks",
        "label": "Риски",
        "question": "Какие риски ты видишь? (например: конкуренты, блокировки, курсы валют, зависимость от одного поставщика)",
        "type": "text",
    },
    {
        "key": "competition",
        "label": "Конкуренция",
        "question": "Как ты оцениваешь конкуренцию? (например: высокая, средняя, низкая, монополия, демпинг)",
        "type": "text",
    },
    {
        "key": "seasonality",
        "label": "Сезонность",
        "question": "Есть ли сезонность у товара? (например: только зима, только лето, круглый год, пики к праздникам)",
        "type": "text",
    },
]


def _parse_float(value: str) -> Optional[float]:
    """Пытаемся аккуратно распарсить число, поддерживая запятую и точку."""
    value = value.strip().replace(" ", "").replace(",", ".")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _format_money(value: float) -> str:
    """Форматируем деньги с двумя знаками после запятой."""
    return f"{value:,.2f}".replace(",", " ")


def _calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Расчёт ключевых показателей:
    - валовая прибыль
    - чистая прибыль
    - маржинальность %
    - точка безубыточности (условная, в штуках)
    """

    purchase_price = float(data.get("purchase_price", 0) or 0)
    sale_price = float(data.get("sale_price", 0) or 0)
    commission_percent = float(data.get("platform_commission_percent", 0) or 0)
    logistics = float(data.get("logistics", 0) or 0)
    delivery = float(data.get("delivery", 0) or 0)
    marketing = float(data.get("marketing", 0) or 0)
    other_expenses = float(data.get("other_expenses", 0) or 0)

    # комиссия в деньгах
    commission_amount = sale_price * commission_percent / 100.0

    # выручка и себестоимость
    revenue = sale_price
    cogs = purchase_price

    gross_profit = revenue - cogs  # валовая прибыль
    variable_costs = commission_amount + logistics + delivery + marketing + other_expenses

    net_profit = gross_profit - variable_costs  # чистая прибыль с единицы
    margin_percent = 0.0
    if sale_price > 0:
        margin_percent = (net_profit / sale_price) * 100.0

    # Условная точка безубыточности:
    # считаем, что все затраты здесь переменные, и считаем,
    # сколько нужно продать единиц, чтобы окупить полную себестоимость.
    total_cost_per_unit = cogs + variable_costs
    if net_profit > 0:
        breakeven_units = round(total_cost_per_unit / net_profit)
    else:
        breakeven_units = 0

    return {
        "commission_amount": commission_amount,
        "revenue": revenue,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "variable_costs": variable_costs,
        "net_profit": net_profit,
        "margin_percent": margin_percent,
        "breakeven_units": breakeven_units,
    }


def _build_human_readable_summary(data: Dict[str, Any], metrics: Dict[str, Any]) -> str:
    """Формируем человеко-читаемый текст таблицы."""
    lines = []
    lines.append("📊 *Artbazar AI Таблица*")
    lines.append("")
    lines.append(f"• Ниша: *{data.get('niche')}*")
    lines.append(f"• Товар: *{data.get('product')}*")
    lines.append("")
    lines.append(f"💰 Закупочная цена: *{_format_money(data['purchase_price'])}*")
    lines.append(f"🏷 Цена продажи: *{_format_money(data['sale_price'])}*")
    lines.append(
        f"🧾 Комиссия площадки: *{data['platform_commission_percent']}%* "
        f"(~{_format_money(metrics['commission_amount'])})"
    )
    lines.append(f"🚚 Логистика: *{_format_money(data['logistics'])}*")
    lines.append(f"📦 Доставка: *{_format_money(data['delivery'])}*")
    lines.append(f"📣 Маркетинг: *{_format_money(data['marketing'])}*")
    lines.append(f"🔧 Прочие расходы: *{_format_money(data['other_expenses'])}*")
    lines.append("")
    lines.append(f"💵 Валовая прибыль: *{_format_money(metrics['gross_profit'])}*")
    lines.append(f"💸 Чистая прибыль: *{_format_money(metrics['net_profit'])}*")
    lines.append(f"📈 Маржинальность: *{metrics['margin_percent']:.2f}%*")
    lines.append(
        f"⚖ Точка безубыточности (условно, в штуках): *{metrics['breakeven_units']}*"
    )
    lines.append("")
    lines.append(f"⚠ Риски: {data.get('risks')}")
    lines.append(f"👥 Конкуренция: {data.get('competition')}")
    lines.append(f"📅 Сезонность: {data.get('seasonality')}")

    return "\n".join(lines)


async def start_artbazar_table(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Точка входа в флоу заполнения таблицы.
    Её должен вызывать /analysis или любая другая команда из user-хендлера.
    """
    # создаём новую сессию
    context.user_data[SESSION_KEY] = {
        "current_index": 0,
        "data": {},
    }

    field = FIELDS[0]
    await update.message.reply_text(
        "Запускаем Artbazar AI Таблицу.\nОтветь на вопросы один за другим.\n\n"
        + field["question"]
    )


async def process_artbazar_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка каждого ответа пользователя.
    Эта функция должна вызываться на КАЖДОЕ текстовое сообщение,
    пока идёт процесс заполнения Artbazar AI Таблицы.
    """
    session = context.user_data.get(SESSION_KEY)

    # Если сессии нет — пользователь написал не в контексте флоу
    if not session:
        await update.message.reply_text(
            "Похоже, ты ещё не запустил Artbazar AI Таблицу.\n"
            "Отправь команду /analysis, чтобы начать."
        )
        return

    text = (update.message.text or "").strip()
    current_index = session["current_index"]
    data = session["data"]

    # Текущий field
    if current_index >= len(FIELDS):
        # На всякий случай — если индекс улетел
        await update.message.reply_text("Таблица уже заполнена. Отправь /analysis заново, чтобы начать новую.")
        context.user_data.pop(SESSION_KEY, None)
        return

    field = FIELDS[current_index]

    # Валидация и сохранение
    if field["type"] == "float":
        value = _parse_float(text)
        if value is None:
            await update.message.reply_text(
                "Нужно указать число. Попробуй ещё раз (можно с точкой или запятой)."
            )
            return
        data[field["key"]] = value
    else:
        # text
        if not text:
            await update.message.reply_text("Поле не может быть пустым. Напиши что-то.")
            return
        data[field["key"]] = text

    # Переход к следующему полю
    session["current_index"] = current_index + 1

    # Если ещё есть поля — задаём следующий вопрос
    if session["current_index"] < len(FIELDS):
        next_field = FIELDS[session["current_index"]]
        await update.message.reply_text(next_field["question"])
        return

    # Если это был последний вопрос — завершаем таблицу
    # Считаем метрики
    metrics = _calculate_metrics(data)
    summary_text = _build_human_readable_summary(data, metrics)

    await update.message.reply_markdown(summary_text)

    # AI-анализ, если модуль подключен
    if analyze_artbazar_table is not None:
        try:
            ai_result: Dict[str, Any] = await analyze_artbazar_table(
                table_data=data,
                metrics=metrics,
                raw_summary=summary_text,
            )

            # Ожидаем, что сервис вернёт дикт с ключами:
            # report, forecast, risks, decision
            report = ai_result.get("report")
            forecast = ai_result.get("forecast")
            risks = ai_result.get("risks")
            decision = ai_result.get("decision")

            parts = ["🧠 *AI-анализ от Artbazar AI*"]
            if report:
                parts.append(f"\n📄 Отчёт:\n{report}")
            if forecast:
                parts.append(f"\n📊 Прогноз:\n{forecast}")
            if risks:
                parts.append(f"\n⚠ Дополнительные риски:\n{risks}")
            if decision:
                parts.append(f"\n✅ Решение: *{decision}*")

            await update.message.reply_markdown("\n".join(parts))

        except Exception as e:
            # Если что-то пошло не так — не роняем флоу
            await update.message.reply_text(
                "Не удалось получить AI-анализ, но расчёты таблицы уже готовы.\n"
                f"Техническая ошибка: {e}"
            )
    else:
        # Пока модуль ai_analysis не подключен
        await update.message.reply_text(
            "AI-анализ пока не подключен. Таблица и расчёты уже готовы.\n"
            "Позже здесь будет умный отчёт от Artbazar AI."
        )

    # Чистим сессию после завершения
    context.user_data.pop(SESSION_KEY, None)
