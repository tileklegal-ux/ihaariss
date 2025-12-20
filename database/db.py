# НОВЫЙ db.py
import os
import time
import logging
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Connection pool для Railway
connection_pool = None

def init_db_pool():
    """Инициализация пула подключений"""
    global connection_pool
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # min connections
            10, # max connections  
            DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        logger.info("Database pool initialized")
        
        # Проверяем существование всех таблиц
        _ensure_tables()
        
    except Exception as e:
        logger.error(f"Failed to init DB pool: {e}")
        raise

@contextmanager
def get_cursor():
    """Безопасное получение курсора из пула"""
    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn.cursor()
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"DB error: {e}")
        raise
    finally:
        if conn:
            connection_pool.putconn(conn)

def _ensure_tables():
    """Проверяем и создаём таблицы если нужно"""
    with get_cursor() as cur:
        # Таблица users
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                role TEXT NOT NULL DEFAULT 'user',
                premium_until TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        # Таблица analysis (если её нет)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS analysis (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                analysis_type TEXT NOT NULL,  -- 'product', 'niche', 'business'
                data JSONB NOT NULL,
                insights TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                INDEX idx_user_analysis (user_id, analysis_type)
            )
        """)
        
        # Таблица history (логи действий)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                action TEXT NOT NULL,  -- 'premium_activated', 'ai_request', 'export'
                details JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        logger.info("All tables verified/created")

# Остальные функции переписать для работы с пулом...

def ensure_user_exists(user_id: int, username: str = None):
    """Оптимизированная версия с UPSERT"""
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO users (user_id, username, role)
            VALUES (%s, %s, 'user')
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                username = EXCLUDED.username,
                updated_at = NOW()
            WHERE users.username != EXCLUDED.username
        """, (user_id, username or ""))
