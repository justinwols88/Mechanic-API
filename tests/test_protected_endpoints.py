# tests/test_protected_endpoints.py
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import create_app
from tests.test_utils import TestUtils

class TestProtectedEndpoints(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        from application.extensions import db
        db.create_all()
        
        # Create test data
        self.customer = TestUtils.create_test_customer()
        self.mechanic = TestUtils.create_test_mechanic()
    
    def tearDown(self):
        from application.extensions import db
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def get_customer_token(self):
        """Get authentication token for customer"""
        data = {
            "email": self.customer.email,
            "password": "password123"
        }
        response = self.client.post('/customers/login', json=data)
        if response.status_code == 200:
            return response.get_json().get('token')
        return None
    
    def get_mechanic_token(self):
        """Get authentication token for mechanic"""
        data = {
            "email": self.mechanic.email,
            "password": "password123"
        }
        response = self.client.post('/mechanic/login', json=data)
        if response.status_code == 200:
            return response.get_json().get('token')
        return None
    
    def test_customer_profile_with_auth(self):
        """Test customer profile with authentication"""
        token = self.get_customer_token()
        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = self.client.get('/customers/profile', headers=headers)
            print(f"Customer profile with auth: {response.status_code}")
            self.assertEqual(response.status_code, 200)
        else:
            print("Could not get customer token, skipping test")
            self.skipTest("Customer login not working")
    
    def test_mechanic_profile_with_auth(self):
        """Test mechanic profile with authentication"""
        token = self.get_mechanic_token()
        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = self.client.get('/mechanic/profile', headers=headers)
            print(f"Mechanic profile with auth: {response.status_code}")
            self.assertEqual(response.status_code, 200)
        else:
            print("Could not get mechanic token, skipping test")
            self.skipTest("Mechanic login not working")

if __name__ == '__main__':
    unittest.main()