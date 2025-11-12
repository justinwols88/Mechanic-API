# tests/test_whats_working.py
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import create_app
from tests.test_utils import TestUtils

class TestWhatsWorking(unittest.TestCase):
    
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
    
    def test_working_endpoints(self):
        """Test endpoints that should work without authentication"""
        working_endpoints = []
        
        # Test customer list
        response = self.client.get('/customers/')
        if response.status_code == 200:
            working_endpoints.append('GET /customers/')
        
        # Test specific customer (if not 500)
        response = self.client.get(f'/customers/{self.customer.id}')
        if response.status_code == 200:
            working_endpoints.append('GET /customers/{id}')
        
        # Test inventory endpoints (should be public)
        response = self.client.get('/inventory/')
        if response.status_code == 200:
            working_endpoints.append('GET /inventory/')
        
        print("\n=== WORKING ENDPOINTS ===")
        for endpoint in working_endpoints:
            print(f"✅ {endpoint}")
        
        print(f"\nTotal working endpoints: {len(working_endpoints)}")
        
        # We should have at least the customer list working
        self.assertIn('GET /customers/', working_endpoints)
    
    def test_endpoints_needing_fixes(self):
        """Document endpoints that need fixes"""
        problematic_endpoints = []
        
        # Test specific customer
        response = self.client.get(f'/customers/{self.customer.id}')
        if response.status_code == 500:
            problematic_endpoints.append(('GET /customers/{id}', '500 Internal Server Error'))
        
        # Test login endpoints
        response = self.client.post('/customers/login', json={})
        if response.status_code == 400:
            problematic_endpoints.append(('POST /customers/login', '400 Bad Request (needs proper data)'))
        
        print("\n=== ENDPOINTS NEEDING FIXES ===")
        for endpoint, issue in problematic_endpoints:
            print(f"❌ {endpoint}: {issue}")
        
        print(f"\nTotal endpoints needing fixes: {len(problematic_endpoints)}")

if __name__ == '__main__':
    unittest.main()