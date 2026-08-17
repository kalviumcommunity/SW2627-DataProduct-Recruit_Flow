from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
import app.models as models
import app.schemas as schemas

# Configure OAuth2PasswordBearer. FastAPI will look for the 'Authorization: Bearer <token>' header.
# We point tokenUrl to '/login', which is where clients will send credentials to fetch a token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 1. Helper function to verify a plain text password against its stored hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

# 2. Helper function to generate a secure bcrypt hash of a plain text password
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

# 3. Helper function to generate a signed JSON Web Token (JWT)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    
    # Calculate token expiration timestamp
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    # Add expiration claim ('exp') to payload
    to_encode.update({"exp": expire})
    
    # Sign the token using our Secret Key and Algorithm
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 4. Dependency to retrieve and verify the currently logged-in user.
# Protected routes will declare this as a dependency: active_user: models.User = Depends(get_current_user)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token using our Secret Key
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub") # 'sub' is the standard subject claim containing user identifier (email)
        
        if email is None:
            raise credentials_exception
            
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    # Query the database to find the user matching the email
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
        
    return user
