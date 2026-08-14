import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.engine.url import make_url
from app.config import settings

def create_recruitment_db():
    # Parse the DATABASE_URL using SQLAlchemy's make_url
    # This automatically decodes URL characters like '%40' to '@'
    url = make_url(settings.DATABASE_URL)
    
    db_name = url.database
    username = url.username
    password = url.password
    host = url.host or "localhost"
    port = url.port or "5432"

    print(f"Connecting to PostgreSQL default instance on {host}:{port} as user '{username}'...")
    try:
        # Connect to 'postgres' default database first to create 'recruitment_db'
        conn = psycopg2.connect(
            dbname="postgres",
            user=username,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}';")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Database '{db_name}' does not exist. Creating database...")
            cursor.execute(f"CREATE DATABASE {db_name};")
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")
            
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print("\nERROR: Failed to connect to local PostgreSQL instance.")
        print(f"Details: {e}")
        return False

if __name__ == "__main__":
    create_recruitment_db()
