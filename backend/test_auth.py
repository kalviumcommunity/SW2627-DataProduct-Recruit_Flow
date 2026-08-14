import sys
import os
from datetime import timedelta
# Add the backend folder to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.auth import get_password_hash, verify_password, create_access_token
from jose import jwt
from app.config import settings

def test_auth_utilities():
    print("--- Testing Cryptography & JWT Utilities ---")

    # Test 1: Hashing & Verification
    plain_password = "my_super_secure_password"
    print(f"\nTest 1: Hashing password: '{plain_password}'...")
    hashed = get_password_hash(plain_password)
    
    print(f"SUCCESS: Password hashed!")
    print(f"  Hashed Value: {hashed}")
    
    # Verify that the hashed password is not plain text
    assert hashed != plain_password
    assert len(hashed) > 10
    
    # Test verification
    print("\nVerifying correct password...")
    is_correct = verify_password(plain_password, hashed)
    print(f"  Result: {is_correct} (Expected: True)")
    assert is_correct is True
    
    print("Verifying incorrect password...")
    is_incorrect = verify_password("wrong_password", hashed)
    print(f"  Result: {is_incorrect} (Expected: False)")
    assert is_incorrect is False
    print("SUCCESS: Hashing and password verification functions are working!")

    # Test 2: JWT Access Token Creation and Decoding
    test_email = "vansh@example.com"
    print(f"\nTest 2: Creating JWT Access Token for: '{test_email}'...")
    
    # JWT standard claim 'sub' (subject) holds the unique identifier, which is the user email
    token = create_access_token(data={"sub": test_email}, expires_delta=timedelta(minutes=15))
    print(f"SUCCESS: JWT Token created!")
    print(f"  Token: {token}")
    
    print("\nDecoding and verifying JWT Token...")
    try:
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        decoded_email = decoded_payload.get("sub")
        print(f"  Decoded Email: {decoded_email} (Expected: {test_email})")
        assert decoded_email == test_email
        print("SUCCESS: JWT generation, signing, and verification are working successfully!")
    except Exception as e:
        print(f"FAIL: Token decoding failed. Error: {e}")

if __name__ == "__main__":
    test_auth_utilities()
