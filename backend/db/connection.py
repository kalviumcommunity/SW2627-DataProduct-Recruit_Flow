import os
from typing import Dict, Any

def get_db_connection_params() -> Dict[str, Any]:
    """Returns database connection parameters from environment variables."""
    return {
        "dbname": os.getenv("POSTGRES_DB", "recruitflow"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
    }

def get_connection():
    """Establishes a PostgreSQL database connection if driver is available."""
    try:
        import psycopg2
        params = get_db_connection_params()
        return psycopg2.connect(**params)
    except Exception as e:
        print(f"PostgreSQL connection offline: {e}")
        return None
