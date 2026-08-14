# backend/app/core/database.py
import psycopg2
from contextlib import contextmanager
from app.core.config import settings

@contextmanager
def get_connection():
    conn = psycopg2.connect(settings.DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()
