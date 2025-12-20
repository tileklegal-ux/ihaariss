# services/openai_client.py
import logging
import asyncio
from openai import AsyncOpenAI, APITimeoutError
import os

logger = logging.getLogger(__name__)

# Базовые паттерны защиты
INJECTION_PATTERNS = [
    "ignore all previous",
    "disregard your system",
    "you are now",
    "role play as",
    "забудь всё что было",
    "игнорируй предыдущие инструкции",
]

MAX_PROMPT_LENGTH = 2000
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY не установлен")
        self.client = AsyncOpenAI(api_key=api_key, timeout=REQUEST_TIMEOUT)
        
    def _check_injection(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()
        for pattern in INJECTION_PATTERNS:
            if pattern in prompt_lower:
                return True
        if len(prompt) > MAX_PROMPT_LENGTH:
            return True
        return False
    
    async def ask(self, prompt: str) -> str:
        if not prompt or len(prompt.strip()) < 5:
            return "Запрос слишком короткий."
        
        if len(prompt) > MAX_PROMPT_LENGTH:
            logger.warning(f"Prompt too long: {len(prompt)} chars")
            return "Запрос слишком длинный. Сократите до 2000 символов."
        
        if self._check_injection(prompt):
            logger.warning(f"Injection attempt: {prompt[:100]}")
            return "Запрос заблокирован системой безопасности."
        
        system_prompt = (
            "Ты — аналитик-консультант для предпринимателей. "
            "Твоя роль: предоставлять структурированные наблюдения, "
            "выявлять риски и предлагать варианты проверки. "
            "ЗАПРЕЩЕНО: давать советы, обещания, прогнозы, рекомендации. "
            "Формат: факты → риски → проверки. "
            "Завершай фразой: 'Это аналитический ориентир, решение за вами.'"
        )
        
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=800,
                )
                
                answer = response.choices[0].message.content.strip()
                logger.info(f"OpenAI request: {len(prompt)} chars → {len(answer)} chars")
                return answer
                
            except APITimeoutError:
                if attempt == MAX_RETRIES:
                    return "Превышено время ожидания ответа."
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                if attempt == MAX_RETRIES:
                    return "Временная ошибка сервиса анализа."
                await asyncio.sleep(2)
        
        return "Не удалось получить ответ."

_service = OpenAIService()

async def ask_openai(prompt: str) -> str:
    return await _service.ask(prompt)
