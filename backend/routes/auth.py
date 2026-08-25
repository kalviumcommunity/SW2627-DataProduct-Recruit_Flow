from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, HTTPException, status, Depends
from backend.services.auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class SignupRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    full_name: Optional[str] = Field(None, description="Full Name of the HR user")
    role: Optional[str] = Field("hr_user", description="User role (e.g. hr_user, hr_admin)")

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(req: SignupRequest):
    """
    Registers a new HR user account with hashed password.
    """
    if not req.email or "@" not in req.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid email address is required."
        )
    if len(req.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )
        
    user = register_user(
        email=req.email,
        password=req.password,
        full_name=req.full_name,
        role=req.role or "hr_user"
    )
    
    # Generate token immediately upon signup
    access_token = create_access_token(data={"sub": user["email"], "role": user["role"]})
    
    return {
        "status": "success",
        "message": "User registered successfully.",
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login")
async def login(req: LoginRequest):
    """
    Authenticates HR user credentials and returns a JWT access token.
    """
    user = authenticate_user(email=req.email, password=req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    access_token = create_access_token(data={"sub": user["email"], "role": user.get("role", "hr_user")})
    
    return {
        "status": "success",
        "message": "Login successful.",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "role": user.get("role", "hr_user")
        }
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Retrieves the currently authenticated HR user's profile.
    """
    return {
        "status": "success",
        "user": {
            "id": current_user["id"],
            "email": current_user["email"],
            "full_name": current_user.get("full_name", ""),
            "role": current_user.get("role", "hr_user")
        }
    }
