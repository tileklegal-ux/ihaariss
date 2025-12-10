from telegram import Update
from telegram.ext import ContextTypes

# Полный список полей, заполняемых пользователем
FIELDS = [
    ("niche", "Введите нишу товара:"),
    ("product", "Введите название товара:"),
    ("purchase_price", "Введите закупочную цену:"),
    ("sale_price", "Введите цену продажи:"),
    ("commission_percent", "Введите комиссию площадки (%):"),
    ("logistics_cost", "Введите расходы на логистику:"),
    ("delivery_cost", "Введите расходы на доставку:"),
    ("marketing_cost", "Введите маркетинг:"),
    ("other_costs", "Введите прочие расходы:"),
    ("risks", "Опишите риски:"),
    ("competition", "Уровень конкуренции:"),
    ("seasonality", "Определите сезонность:")
]


async def ask_next(update, context, index):
    """Запрашивает следующий вопрос"""
    field_name, question = FIELDS[index]
    context.user_data["current_field"] = field_name
    await update.message.reply_text(question)


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает входящие ответы пользователя"""

    user_data = context.user_data
    current_field = user_data.get("current_field")
    answers = user_data.setdefault("answers", {})
    index = user_data.get("field_index", 0)

    # сохраняем ответ
    if current_field:
        answers[current_field] = update.message.text

    # идём к следующему шагу
    index += 1

    # если всё заполнено → возвращаем данные
    if index >= len(FIELDS):
        context.user_data.clear()
        return answers, True

    # продолжаем задавать вопросы
    user_data["field_index"] = index
    await ask_next(update, context, index)
    return answers, False


async def start_table_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Главная функция диалога.
    Возвращает:
    - table_data: dict
    - metrics: dict
    - summary: текстовое описание
    """

    # Начинаем с первого вопроса
    context.user_data["field_index"] = 0
    context.user_data["answers"] = {}

    first_field, first_question = FIELDS[0]
    context.user_data["current_field"] = first_field

    await update.message.reply_text(first_question)

    # Основной цикл ожидания реакции
    while True:
        response = await context.application.wait_for_update()
        if response.message:
            answers, finished = await process_message(response.message, context)
            if finished:
                break

    # Преобразуем ответы
    table = {
        "Ниша": answers.get("niche"),
        "Товар": answers.get("product"),
        "Закупочная цена": float(answers.get("purchase_price", 0)),
        "Цена продажи": float(answers.get("sale_price", 0)),
        "Комиссия (%)": float(answers.get("commission_percent", 0)),
        "Логистика": float(answers.get("logistics_cost", 0)),
        "Доставка": float(answers.get("delivery_cost", 0)),
        "Маркетинг": float(answers.get("marketing_cost", 0)),
        "Прочие расходы": float(answers.get("other_costs", 0)),
        "Риски": answers.get("risks"),
        "Конкуренция": answers.get("competition"),
        "Сезонность": answers.get("seasonality"),
    }

    # Генерируем базовые метрики
    commission_value = table["Цена продажи"] * (table["Комиссия (%)"] / 100)
    gross_profit = table["Цена продажи"] - table["Закупочная цена"]
    net_profit = gross_profit - (
        commission_value
        + table["Логистика"]
        + table["Доставка"]
        + table["Маркетинг"]
        + table["Прочие расходы"]
    )

    metrics = {
        "commission_value": commission_value,
        "gross_profit": gross_profit,
        "net_profit": net_profit,
        "margin_percent": round((net_profit / table["Цена продажи"]) * 100, 2) if table["Цена продажи"] else 0,
        "breakeven_units": 1 if net_profit > 0 else 9999,
    }

    summary = (
        f"Ниша: {table['Ниша']}\n"
        f"Товар: {table['Товар']}\n"
        f"Закуп: {table['Закупочная цена']}\n"
        f"Продажа: {table['Цена продажи']}\n"
        f"Риски: {table['Риски']}\n"
        f"Конкуренция: {table['Конкуренция']}\n"
        f"Сезонность: {table['Сезонность']}\n"
    )

    return table, metrics, summary
