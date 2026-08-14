import json
import urllib.request
import urllib.error
import random

BASE_URL = "http://127.0.0.1:8000"

def send_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    req_data = None
    if data is not None:
        if isinstance(data, dict):
            if headers.get("Content-Type") == "application/x-www-form-urlencoded":
                req_data = urllib.parse.urlencode(data).encode("utf-8")
            else:
                req_data = json.dumps(data).encode("utf-8")
                headers["Content-Type"] = "application/json"
        else:
            req_data = data
            
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8"))
        except Exception:
            err_body = e.reason
        return e.code, err_body

def run_tests():
    print("=== Testing FastAPI Auth Endpoints ===")
    
    # Generate a unique email for this test run to prevent conflict with prior runs
    random_num = random.randint(1000, 9999)
    test_email = f"user_{random_num}@example.com"
    test_password = "password123"
    test_name = "Vansh Bhandari"
    
    # 1. Test POST /signup
    print(f"\n1. Testing /signup with email: '{test_email}'...")
    signup_data = {
        "email": test_email,
        "password": test_password,
        "full_name": test_name
    }
    status, body = send_request(f"{BASE_URL}/signup", method="POST", data=signup_data)
    print(f"   Status Code: {status}")
    print(f"   Response: {body}")
    assert status == 201
    assert body["email"] == test_email
    assert "id" in body
    assert "password" not in body
    assert "hashed_password" not in body
    print("   SUCCESS: Registration created and password fields omitted from response.")
    
    # 2. Test POST /signup with duplicate email
    print(f"\n2. Testing /signup duplicate email detection...")
    status, body = send_request(f"{BASE_URL}/signup", method="POST", data=signup_data)
    print(f"   Status Code: {status}")
    print(f"   Response: {body}")
    assert status == 400
    assert body["detail"] == "Email already registered"
    print("   SUCCESS: Duplicate signup successfully blocked with HTTP 400.")

    # 3. Test POST /login with correct password
    print(f"\n3. Testing /login with correct credentials...")
    login_data = {
        "username": test_email, # OAuth2 request form expects 'username' for email
        "password": test_password
    }
    status, body = send_request(
        f"{BASE_URL}/login", 
        method="POST", 
        data=login_data, 
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"   Status Code: {status}")
    print(f"   Response: {body}")
    assert status == 200
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    token = body["access_token"]
    print("   SUCCESS: JWT access token generated successfully.")

    # 4. Test POST /login with incorrect password
    print(f"\n4. Testing /login with incorrect password...")
    invalid_login_data = {
        "username": test_email,
        "password": "wrong_password_here"
    }
    status, body = send_request(
        f"{BASE_URL}/login", 
        method="POST", 
        data=invalid_login_data, 
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"   Status Code: {status}")
    print(f"   Response: {body}")
    assert status == 401
    assert body["detail"] == "Invalid credentials"
    print("   SUCCESS: Invalid login blocked with HTTP 401.")

    # 5. Test GET /users/me with valid JWT token
    print(f"\n5. Testing /users/me with valid Bearer token...")
    status, body = send_request(
        f"{BASE_URL}/users/me", 
        method="GET", 
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"   Status Code: {status}")
    print(f"   Response: {body}")
    assert status == 200
    assert body["email"] == test_email
    assert body["full_name"] == test_name
    print("   SUCCESS: Successfully accessed protected endpoint. User profile returned.")

    # 6. Test GET /users/me with invalid JWT token
    print(f"\n6. Testing /users/me with invalid token...")
    status, body = send_request(
        f"{BASE_URL}/users/me", 
        method="GET", 
        headers={"Authorization": "Bearer invalid_token_xyz"}
    )
    print(f"   Status Code: {status}")
    print(f"   Response: {body}")
    assert status == 401
    assert body["detail"] == "Could not validate credentials"
    print("   SUCCESS: Unauthenticated access blocked with HTTP 401.")

    print("\nALL ENDPOINT TESTS PASSED SUCCESSFULLY! AUTHENTICATION SYSTEM IS 100% WORKING!")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\nTEST RUN FAILED: {e}")
