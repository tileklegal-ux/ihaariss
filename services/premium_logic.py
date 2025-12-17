from datetime import datetime, timedelta, timezone
from database.db import (
    get_user,
    update_premium_until,
    remove_premium_from_db,
)

def set_premium(user_id: int, days: int = 30) -> None:
    now = datetime.now(timezone.utc)
    premium_until = now + timedelta(days=days)
    update_premium_until(user_id, premium_until)

def extend_premium(user_id: int, days: int) -> None:
    user = get_user(user_id)
    now = datetime.now(timezone.utc)

    if user and user.get("premium_until") and user["premium_until"] > now:
        premium_until = user["premium_until"] + timedelta(days=days)
    else:
        premium_until = now + timedelta(days=days)

    update_premium_until(user_id, premium_until)

def remove_premium(user_id: int) -> None:
    remove_premium_from_db(user_id)
