# tests/test_debug_customer.py
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import create_app
from tests.test_utils import TestUtils


class TestDebugCustomer(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        from application.extensions import db
        db.create_all()
        
        # Create test customer
        self.customer = TestUtils.create_test_customer()
        self.customer_id = self.customer.id
    
    def tearDown(self):
        from application.extensions import db
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_specific_customer_debug(self):
        """Debug the specific customer endpoint"""
        response = self.client.get(f'/customers/{self.customer_id}')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 500:
            error_data = response.get_json()
            print(f"500 Error details: {error_data}")
            
            # Check if it's a serialization issue
            from application.models import Customer
            customer = Customer.query.get(self.customer_id)
            print(f"Customer object: {customer}")
            print(f"Customer email: {customer.email}")
            
            # Try to serialize manually
            try:
                serialized = {
                    'id': customer.id,
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'email': customer.email
                }
                print(f"Manual serialization: {serialized}")
            except Exception as e:
                print(f"Serialization error: {e}")

if __name__ == '__main__':
    unittest.main()