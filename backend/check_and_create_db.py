import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def check_and_create():
    # Connection details for default database
    db_name = "recruitment_db"
    user = "postgres"
    password = "postgres"
    host = "localhost"
    port = "5432"

    print("Connecting to PostgreSQL default instance...")
    try:
        # Connect to 'postgres' default database first to check/create the target database
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
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
        print("\nPossible reasons:")
        print("1. The password set during installation is not 'postgres'.")
        print("2. The username is not 'postgres'.")
        print("\nIf you used a different password, please update it in your 'backend/.env' file.")
        return False

if __name__ == "__main__":
    check_and_create()
