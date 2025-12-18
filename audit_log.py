import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def log_event(event: str, user_id: int | None = None, extra: dict | None = None):
    """
    Универсальный аудит-лог.
    Ничего не ломает, всегда безопасен.
    """

    payload = {
        "time": datetime.utcnow().isoformat(),
        "event": event,
        "user_id": user_id,
        "extra": extra or {},
    }

    logging.info(f"AUDIT | {payload}")
