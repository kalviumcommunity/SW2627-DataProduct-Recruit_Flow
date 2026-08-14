from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# 1. Base User Schema holding shared fields
class UserBase(BaseModel):
    email: str = Field(..., description="The user's email address")
    full_name: Optional[str] = Field(None, description="The user's full name")

# 2. Schema for validating User Registration input
class UserCreate(UserBase):
    # Enforce minimum 8-character passwords for security
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

# 3. Schema for formatting User details in API Responses
class UserOut(UserBase):
    id: int
    created_at: datetime

    # Pydantic v2 ORM configuration. 
    # Allows Pydantic to parse SQLAlchemy models directly into this schema structure.
    model_config = ConfigDict(from_attributes=True)

# 4. Schema for returned login JWT tokens
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# 5. Schema for representing decoded JWT token payload
class TokenData(BaseModel):
    email: Optional[str] = None
