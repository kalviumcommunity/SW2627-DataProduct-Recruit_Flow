from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Create the SQLAlchemy engine that connects Python to PostgreSQL
# We retrieve the connection string from settings
engine = create_engine(settings.DATABASE_URL)

# Create a SessionLocal class. Each instance of this class will be a database session.
# - autocommit=False: Transactions are not committed automatically, allowing us to manage commits manually.
# - autoflush=False: Queries do not automatically flush changes to the database before executing.
# - bind=engine: Bind the sessions to our database engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for database models to inherit from.
# SQLAlchemy uses this base class to map Python classes to database tables.
Base = declarative_base()

# Dependency to manage database sessions during API requests.
# It yields a database session to the route and ensures it gets closed after the response is sent.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
