import os
import json
import uuid
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.db.connection import get_connection

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "recruitflow-super-secret-jwt-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
USERS_JSON_PATH = os.path.join(PROCESSED_DIR, "users_auth_store.json")

security = HTTPBearer(auto_error=False)

def _load_fallback_users() -> Dict[str, Any]:
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    if os.path.exists(USERS_JSON_PATH):
        try:
            with open(USERS_JSON_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_fallback_users(users: Dict[str, Any]):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    with open(USERS_JSON_PATH, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetches user record by email from PostgreSQL or fallback store."""
    email_clean = email.strip().lower()
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, hashed_password, full_name, role FROM core.users WHERE LOWER(email) = %s", (email_clean,))
                row = cur.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "email": row[1],
                        "hashed_password": row[2],
                        "full_name": row[3],
                        "role": row[4]
                    }
        except Exception as e:
            print(f"Error querying users from DB: {e}")
        finally:
            conn.close()
            
    # Fallback to persistent JSON store
    users = _load_fallback_users()
    return users.get(email_clean)

def register_user(email: str, password: str, full_name: Optional[str] = None, role: str = "hr_user") -> Dict[str, Any]:
    """Registers a new user in PostgreSQL or fallback store."""
    email_clean = email.strip().lower()
    if get_user_by_email(email_clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
        
    hashed = hash_password(password)
    user_id = None
    
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO core.users (email, hashed_password, full_name, role)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (email_clean, hashed, full_name or "", role))
                user_id = cur.fetchone()[0]
                conn.commit()
        except Exception as e:
            print(f"Error inserting user into DB: {e}")
        finally:
            conn.close()
            
    if not user_id:
        user_id = str(uuid.uuid4())
        
    # Always sync to fallback store
    users = _load_fallback_users()
    users[email_clean] = {
        "id": user_id,
        "email": email_clean,
        "hashed_password": hashed,
        "full_name": full_name or "",
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _save_fallback_users(users)
    
    return {
        "id": user_id,
        "email": email_clean,
        "full_name": full_name or "",
        "role": role
    }

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticates email and password, returning user dictionary or None."""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to extract and verify the current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    user = get_user_by_email(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user
