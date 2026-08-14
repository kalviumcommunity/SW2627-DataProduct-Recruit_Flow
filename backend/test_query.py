import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect
from app.config import settings

def inspect_tables():
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("Tables in recruitment_db:")
        for table in tables:
            print(f"- {table}")
            # List columns in the table
            columns = inspector.get_columns(table)
            for col in columns:
                print(f"  * {col['name']} ({col['type']})")
        
        if "users" in tables:
            print("\nSUCCESS: The 'users' table exists and is fully working!")
            return True
        else:
            print("\nWARNING: Connection succeeded, but the 'users' table was not found.")
            return False
    except Exception as e:
        print(f"Error during inspection: {e}")
        return False

if __name__ == "__main__":
    inspect_tables()
