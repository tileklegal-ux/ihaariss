import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN / BOT_TOKEN is not set")

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "database/artbazar.db")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

FREE_AI_LIMIT = int(os.getenv("FREE_AI_LIMIT", "5"))
PREMIUM_AI_LIMIT = int(os.getenv("PREMIUM_AI_LIMIT", "500"))

ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
TIMEZONE = os.getenv("TIMEZONE", "UTC")
