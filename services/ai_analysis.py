import os
import json
from typing import Dict, Any

from openai import OpenAI

# Новый клиент OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _build_prompt(table_data: Dict[str, Any], metrics: Dict[str, Any], raw_summary: str) -> str:
    """
    Собираем промпт для модели.
    Возвращаем текст, который будет отправлен в messages.
    """

    base_info = {
        "table": table_data,
        "metrics": metrics,
    }

    prompt = f"""
Ты — эксперт по юнит-экономике, маркетплейсам и малому бизнесу в Кыргызстане и Казахстане.
Анализируешь нишу и товар по данным Artbazar AI.

Данные (JSON):
{json.dumps(base_info, ensure_ascii=False, indent=2)}

Сводная таблица:
\"\"\"
{raw_summary}
\"\"\"

Верни строго JSON следующего вида:

{{
  "report": "...",
  "forecast": "...",
  "risks": "...",
  "decision": "стоит заходить" | "есть смысл протестировать" | "не стоит заходить"
}}

Не пиши ничего вне JSON. Не используй markdown.
"""

    return prompt


def _call_openai(prompt: str) -> Dict[str, Any]:
    """
    Вызов нового OpenAI API.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты строгий, но понятный бизнес-аналитик. "
                        "Помогаешь предпринимателям принимать решения о нише и товаре."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=900,
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        return {
            "report": data.get("report", "").strip(),
            "forecast": data.get("forecast", "").strip(),
            "risks": data.get("risks", "").strip(),
            "decision": data.get("decision", "").strip(),
        }

    except Exception as e:
        return {
            "report": f"AI-анализ временно недоступен (ошибка: {e})",
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
    Основная функция анализа Artbazar AI Таблицы.
    """
    prompt = _build_prompt(table_data, metrics, raw_summary)
    return _call_openai(prompt)
