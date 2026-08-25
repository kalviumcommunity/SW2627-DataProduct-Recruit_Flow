import os
import sys
import unittest
from starlette.testclient import TestClient

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.app import app

client = TestClient(app)

class TestAuthAndBatches(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_email = "hr_test_lead@recruitflow.com"
        cls.test_password = "SecurePassword123!"
        cls.test_name = "Sarah Jenkins"

    def test_01_signup_success(self):
        payload = {
            "email": self.test_email,
            "password": self.test_password,
            "full_name": self.test_name,
            "role": "hr_manager"
        }
        response = client.post("/api/auth/signup", json=payload)
        # Should be 201 or 400 if already created in earlier test run
        self.assertIn(response.status_code, [201, 400])
        if response.status_code == 201:
            data = response.json()
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["user"]["email"], self.test_email)
            self.assertIn("access_token", data)

    def test_02_login_invalid_password(self):
        payload = {
            "email": self.test_email,
            "password": "WrongPassword999!"
        }
        response = client.post("/api/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid email or password", response.json()["detail"])

    def test_03_login_success_and_jwt_token(self):
        payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        response = client.post("/api/auth/login", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["user"]["email"], self.test_email)
        
        # Test /api/auth/me with token
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        me_resp = client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_resp.status_code, 200)
        self.assertEqual(me_resp.json()["user"]["email"], self.test_email)

    def test_04_batches_lifecycle(self):
        # 1. Create a new batch (Option 1)
        create_payload = {"batch_name": "Q1_2026_Engineering_Hiring_Drive"}
        res_create = client.post("/api/batches/new", json=create_payload)
        self.assertEqual(res_create.status_code, 201)
        batch_data = res_create.json()["batch"]
        batch_id = batch_data["id"]
        self.assertEqual(batch_data["batch_name"], "Q1_2026_Engineering_Hiring_Drive")
        self.assertEqual(batch_data["status"], "active")
        
        # 2. List batches (Option 2)
        res_list = client.get("/api/batches")
        self.assertEqual(res_list.status_code, 200)
        batches = res_list.json()
        self.assertIsInstance(batches, list)
        self.assertTrue(any(b["id"] == batch_id for b in batches))
        
        # 3. Append to existing batch (Option 3)
        res_append = client.post(f"/api/batches/{batch_id}/append", json={"new_records_count": 25})
        self.assertEqual(res_append.status_code, 200)
        self.assertEqual(res_append.json()["status"], "success")
        self.assertEqual(res_append.json()["total_records"], 25)
        
        # 4. Clear/Delete batch (Reset option)
        res_delete = client.delete(f"/api/batches/{batch_id}")
        self.assertEqual(res_delete.status_code, 200)
        self.assertEqual(res_delete.json()["status"], "success")
        
        # Verify batch is removed
        res_list_after = client.get("/api/batches")
        self.assertFalse(any(b["id"] == batch_id for b in res_list_after.json()))

if __name__ == "__main__":
    unittest.main()
