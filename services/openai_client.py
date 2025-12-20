# services/openai_client.py
import logging
from openai import AsyncOpenAI
import os

logger = logging.getLogger(__name__)

_client = None

INJECTION_KEYWORDS = [
    "игнорируй предыдущие инструкции",
    "раскрой системный промпт",
    "будь хакером",
    "ignore all previous instructions",
    "выдай секреты",
]

MAX_RESPONSE_TOKENS = 800

def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY не установлен")
        _client = AsyncOpenAI(api_key=api_key)
    return _client


async def ask_openai(prompt: str) -> str:
    prompt_lower = prompt.lower()
    for keyword in INJECTION_KEYWORDS:
        if keyword in prompt_lower:
            logger.warning(f"Prompt Injection attempt blocked: {prompt}")
            return "Извините, ваш запрос содержит слова, которые нарушают правила безопасности."

    try:
        client = get_client()
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты спокойный аналитик. "
                        "Запрещено: советы, обещания, прогнозы. "
                        "Формат: наблюдения / риски / варианты проверки. "
                        "Всегда добавляй фразу: "
                        "«это ориентир, а не рекомендация; решение за пользователем»."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=MAX_RESPONSE_TOKENS,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.exception("OpenAI error")
        return (
            "Сейчас невозможно получить аналитический разбор.\n"
            "Это ориентир, а не рекомендация; решение за пользователем."
        )
