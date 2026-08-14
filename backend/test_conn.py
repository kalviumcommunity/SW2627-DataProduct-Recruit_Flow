import sys
import os
# Add the backend folder to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings

def test_db_connection():
    print(f"Loaded DATABASE_URL from .env")
    
    # Try to connect using the configured DATABASE_URL
    try:
        engine = create_engine(settings.DATABASE_URL)
        print("Attempting to connect to PostgreSQL database...")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("\nSUCCESS: Successfully connected to recruitment_db!")
            return True
    except Exception as e:
        print("\nCONNECTION FAILED:")
        print(f"Error detail: {e}")
        
        # If it failed because of the '@' in the password, let's explain how to fix it.
        if "password" in str(e).lower() or "authentication failed" in str(e).lower() or "could not translate host" in str(e).lower():
            print("\nNote: Your password contains special characters like '@'.")
            print("You may need to URL-encode the password. For example, '@' becomes '%40'.")
            print("If your password is 'Vansh26@12postgres', try changing the URL in your .env to:")
            print("DATABASE_URL=postgresql://postgres:Vansh26%4012postgres@localhost:5432/recruitment_db")
        return False

if __name__ == "__main__":
    test_db_connection()
