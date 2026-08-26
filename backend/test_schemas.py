import sys
import os
from datetime import datetime

# Add the backend folder to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.schemas import UserCreate, UserOut
from pydantic import ValidationError

def test_validation():
    print("--- Testing Pydantic Schemas ---")

    # Test 1: Invalid signup input (short password)
    print("\nTest 1: Trying to register with a 5-character password...")
    try:
        UserCreate(email="test@example.com", password="123", full_name="John Doe")
        print("FAIL: Validation should have rejected this password!")
    except ValidationError as e:
        print("SUCCESS: Rejected successfully! Validation error details:")
        # Print the exact validation error message
        for error in e.errors():
            print(f"  Field: {error['loc'][0]} -> Message: {error['msg']}")

    # Test 2: Valid signup input
    print("\nTest 2: Trying to register with a valid 10-character password...")
    try:
        valid_user = UserCreate(email="test@example.com", password="secure12345", full_name="John Doe")
        print("SUCCESS: Validated successfully!")
        print(f"  Validated Data: email={valid_user.email}, full_name={valid_user.full_name}")
    except ValidationError as e:
        print(f"FAIL: Schema rejected valid input. Error: {e}")

    # Test 3: Output serialization (excluding password from response)
    print("\nTest 3: Simulating ORM object and serializing to UserOut...")
    # Mocking a database object
    class MockDbUser:
        id = 1
        email = "test@example.com"
        hashed_password = "this_is_a_hashed_password_hash"
        full_name = "John Doe"
        created_at = datetime.now()

    db_user = MockDbUser()
    
    # Serialize the mock database object into UserOut response schema
    user_out = UserOut.model_validate(db_user)
    print("SUCCESS: Serialized database object!")
    print(f"  Serialized JSON keys: {list(user_out.model_dump().keys())}")
    print(f"  Resulting fields: id={user_out.id}, email={user_out.email}, full_name={user_out.full_name}, created_at={user_out.created_at}")
    
    # Assert that password is not present in output schema keys
    assert "password" not in user_out.model_dump()
    assert "hashed_password" not in user_out.model_dump()
    print("  CONFIRMED: Password and password hash are successfully stripped from response data!")

if __name__ == "__main__":
    test_validation()
