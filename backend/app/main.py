from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta

from app.database import engine, Base, get_db
import app.models as models
import app.schemas as schemas
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user

# @app.get("/")
# async def root():
#     return {"message": "RecruitFlow Data Ingestion API is live"}




# # Import routes later
# # from app.api import upload_routes, health_routes
# # app.include_router(upload_routes.router)

# backend/app/main.py
from fastapi import FastAPI
from app.api import analytics_routes, upload_routes, batch_routes

# Initialize the FastAPI application
app = FastAPI(
    title="Recruitment Funnel Analytics API",
    description="Backend API for Recruitment funnel drop-off analytics & user auth.",
    version="0.1.0"
)

# Automatically create database tables on startup.
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
except Exception as e:
    print(f"Warning: Could not create tables at startup. Database might be unreachable: {e}")

# Include routers
app.include_router(upload_routes.router)
app.include_router(analytics_routes.router)
app.include_router(batch_routes.router)

# Root endpoint to verify if the server is running
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Recruitment Funnel Analytics API",
        "docs_url": "/docs"
    }

# Database connectivity health check route.
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "details": "Successfully connected and executed query on PostgreSQL."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {str(e)}"
        )

# 1. User Signup Route
@app.post("/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
@app.post("/api/auth/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if a user with the same email already exists
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # Securely hash the plain-text password
    hashed_pwd = get_password_hash(user_in.password)
    
    # Create the User record model instance
    db_user = models.User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        full_name=user_in.full_name
    )
    
    # Add and commit to PostgreSQL database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# 2. User Login Route
@app.post("/login", response_model=schemas.Token)
@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Query database for the user by email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Verify user exists and check if the password matches the stored hash
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generate the signed JWT token containing the user's email
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# 3. Protected Route: Retrieve current user's profile
@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
