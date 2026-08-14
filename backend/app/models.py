from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    # Unique identifier for the user (auto-incrementing integer)
    id = Column(Integer, primary_key=True, index=True)
    
    # User's email, must be unique and is indexed for faster query lookups
    email = Column(String, unique=True, index=True, nullable=False)
    
    # Securely hashed password string (never store plain-text passwords!)
    hashed_password = Column(String, nullable=False)
    
    # Full name of the user
    full_name = Column(String, nullable=True)
    
    # Flag to enable/disable user accounts
    is_active = Column(Boolean, default=True)
    
    # Timestamp indicating when the user profile was created, defaults to server time
    created_at = Column(DateTime(timezone=True), server_default=func.now())
