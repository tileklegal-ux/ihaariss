# services/message_intents.py

from enum import Enum
from typing import Optional


class MessageIntent(Enum):
    SOCIAL = "social"
    UNKNOWN = "unknown"


# Простые фразы, которыми люди реагируют как люди, а не как по сценарию
SOCIAL_KEYWORDS = [
    "круто",
    "класс",
    "огонь",
    "🔥",
    "молодец",
    "отлично",
    "супер",
    "спасибо",
    "благодарю",
    "👍",
    "👏",
]


def detect_intent(text: Optional[str]) -> MessageIntent:
    """
    Определяет интент сообщения.
    Сейчас намеренно очень простой детектор.
    """
    if not text:
        return MessageIntent.UNKNOWN

    lowered = text.lower().strip()

    for word in SOCIAL_KEYWORDS:
        if word in lowered:
            return MessageIntent.SOCIAL

    return MessageIntent.UNKNOWN


def get_social_reply() -> str:
    """
    Вежливый человеческий ответ, без сброса сценария.
    """
    return (
        "Спасибо 👍\n"
        "Если хочешь — можешь продолжить отвечать на вопросы, "
        "я дальше помогу разобраться."
    )
