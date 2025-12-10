import os
import json
from typing import Dict, Any

import openai

# Берём ключ из ENV (Railway + локальный .env через load_dotenv в main.py)
openai.api_key = os.getenv("OPENAI_API_KEY")


def _build_prompt(table_data: Dict[str, Any], metrics: Dict[str, Any], raw_summary: str, is_premium: bool) -> str:
    """
    Собираем промпт для модели.
    Формат ответа: JSON с нужными полями.
    """

    base_info = {
        "table": table_data,
        "metrics": metrics,
    }

    # На будущее: если будет BASE-тариф, можно урезать анализ по is_premium
    prompt = f"""
Ты — эксперт по юнит-экономике, маркетплейсам и малому бизнесу в Кыргызстане и Казахстане.
Твоя задача — проанализировать нишу и товар, используя переданные данные таблицы Artbazar AI.

Данные (в формате JSON):
{json.dumps(base_info, ensure_ascii=False, indent=2)}

Человеко-читаемая сводка:
\"\"\"
{raw_summary}
\"\"\"

Профиль пользователя:
- Предприниматель или начинающий предприниматель.
- Регион: Кыргызстан / Казахстан.
- Цель: понять, стоит ли заходить в эту нишу с этим товаром.

Сформируй ОТВЕТ в современном телеграм-формате, но верни его СТРОГО в формате JSON со следующими ключами:

- "report"   : общий аналитический отчёт по нише и товару (1–3 абзаца)
- "forecast" : прогноз по нише/товару (рост/падение, потенциал, горизонт 6–12 месяцев)
- "risks"    : ключевые риски (списком, коротко)
- "decision" : итоговое решение в формате одной фразы:
               "стоит заходить" ИЛИ "есть смысл протестировать" ИЛИ "не стоит заходить"

Важно:
- Пиши конкретно по цифрам, маржинальности и рискам.
- Не извиняйся.
- Не добавляй никакого текста ВНЕ JSON.
- Не используй markdown в JSON. Просто текст.
"""

    return prompt


def _call_openai(prompt: str) -> Dict[str, Any]:
    """
    Вызов OpenAI ChatCompletion.
    Возвращаем dict с ключами report, forecast, risks, decision.
    Если что-то пошло не так — возвращаем минимальный fallback.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты строгий, но понятный бизнес-аналитик. "
                        "Твоя задача — помогать предпринимателям принимать решения о нише и товаре."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=900,
        )

        content = response["choices"][0]["message"]["content"]

        # Пытаемся разобрать JSON
        data = json.loads(content)

        # Гарантируем наличие ключей
        return {
            "report": data.get("report", "").strip(),
            "forecast": data.get("forecast", "").strip(),
            "risks": data.get("risks", "").strip(),
            "decision": data.get("decision", "").strip(),
        }

    except Exception as e:
        # Fallback — если модель вернула не-JSON или упала
        return {
            "report": f"AI-анализ временно недоступен. Техническая ошибка: {e}",
            "forecast": "",
            "risks": "",
            "decision": "",
        }


async def analyze_artbazar_table(
    table_data: Dict[str, Any],
    metrics: Dict[str, Any],
    raw_summary: str,
    is_premium: bool = True,
) -> Dict[str, Any]:
    """
    Основная функция, которую вызывает artbazar_table_flow.
    Сейчас is_premium всегда True (вариант C — все как Premium).
    Позже сюда добавим real premium-логику.
    """

    # На этом этапе просто игнорируем is_premium и делаем полный анализ
    prompt = _build_prompt(table_data, metrics, raw_summary, is_premium=is_premium)

    # Вызов OpenAI синхронный, но для простоты MVP просто вызываем его напрямую.
    # Для больших нагрузок можно вынести в executor.
    result = _call_openai(prompt)
    return result
