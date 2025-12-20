# НОВЫЙ openai_client.py
import logging
import time
from openai import AsyncOpenAI, APITimeoutError
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# 1. РАСШИРЕННАЯ ЗАЩИТА
INJECTION_PATTERNS = [
    # Более 50 паттернов на русском и английском
    "игнорируй предыдущие инструкции", "забудь всё что было", 
    "раскрой системный промпт", "покажи секретные инструкции",
    "ignore all previous", "disregard your system", 
    "you are now", "act as if", "role play as",
    "секретный пароль", "данные пользователей", "взломай систему",
    # ... добавить 40+ других
]

# 2. НАСТРОЙКИ БЕЗОПАСНОСТИ
MAX_PROMPT_LENGTH = 2000  # Не более 2000 символов
REQUEST_TIMEOUT = 30      # 30 секунд максимум
MAX_RETRIES = 2           # 2 попытки при ошибке

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY, timeout=REQUEST_TIMEOUT)
        self.request_count = 0
        
    def _check_injection(self, prompt: str) -> bool:
        """Проверка на injection с расширенной логикой"""
        prompt_lower = prompt.lower()
        
        # Проверка по ключевым словам
        for pattern in INJECTION_PATTERNS:
            if pattern in prompt_lower:
                return True
        
        # Проверка слишком длинных запросов (возможен скрытый промпт)
        if len(prompt) > MAX_PROMPT_LENGTH:
            return True
            
        return False
    
    async def ask(self, prompt: str) -> str:
        """Улучшенная версия с безопасностью и мониторингом"""
        self.request_count += 1
        
        # 1. ВАЛИДАЦИЯ
        if not prompt or len(prompt.strip()) < 5:
            return "Запрос слишком короткий для анализа."
        
        if len(prompt) > MAX_PROMPT_LENGTH:
            logger.warning(f"Prompt too long: {len(prompt)} chars")
            return "Запрос слишком длинный. Сократите до 2000 символов."
        
        # 2. ЗАЩИТА ОТ INJECTION
        if self._check_injection(prompt):
            logger.warning(f"Injection attempt blocked: {prompt[:100]}")
            return "Запрос содержит подозрительные элементы и был заблокирован."
        
        # 3. ПОДГОТОВКА СИСТЕМНОГО ПРОМПТА
        system_prompt = (
            "Ты — аналитик-консультант для предпринимателей. "
            "Твоя роль: предоставлять структурированные наблюдения, "
            "выявлять риски и предлагать варианты проверки. "
            "ЗАПРЕЩЕНО: давать советы, обещания, прогнозы, рекомендации. "
            "ЗАПРЕЩЕНО: утверждать что-либо категорично. "
            "Формат: факты → риски → проверки. "
            "Завершай фразой: 'Это аналитический ориентир, решение за вами.'"
        )
        
        # 4. ЗАПРОС С ПОВТОРНЫМИ ПОПЫТКАМИ
        for attempt in range(MAX_RETRIES + 1):
            try:
                start_time = time.time()
                
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=800,
                    timeout=REQUEST_TIMEOUT,
                )
                
                elapsed = time.time() - start_time
                answer = response.choices[0].message.content.strip()
                
                # 5. ЛОГИРОВАНИЕ ДЛЯ RAILWAY
                logger.info(
                    f"OpenAI request #{self.request_count}: "
                    f"prompt={len(prompt)} chars, "
                    f"response={len(answer)} chars, "
                    f"time={elapsed:.2f}s"
                )
                
                return answer
                
            except APITimeoutError:
                if attempt == MAX_RETRIES:
                    logger.error("OpenAI timeout after retries")
                    return "Превышено время ожидания ответа. Попробуйте позже."
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.exception(f"OpenAI error on attempt {attempt}")
                if attempt == MAX_RETRIES:
                    return "Временная ошибка сервиса анализа. Попробуйте позже."
                await asyncio.sleep(2)
        
        return "Не удалось получить ответ."

# Глобальный инстанс для обратной совместимости
_service = OpenAIService()

async def ask_openai(prompt: str) -> str:
    """Старая функция для обратной совместимости"""
    return await _service.ask(prompt)
