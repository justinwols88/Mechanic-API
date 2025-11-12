# tests/test_all_endpoints.py
import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import create_app
from .test_utils import TestUtils

class TestAllEndpoints(unittest.TestCase):
    
    def setUp(self):
        """Set up test database with proper cache initialization"""
        self.db_fd, self.db_path = tempfile.mkstemp()

        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.db_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'CACHE_TYPE': 'NullCache',  # ✅ Disable cache for tests
        })
    
        self.client = self.app.test_client()

        # Create application context and database
        self.app_context = self.app.app_context()
        self.app_context.push()
    
        # ✅ Initialize cache within app context
        from application.extensions import cache
        cache.init_app(self.app)
    
        from application.extensions import db
        db.create_all()
    
    def tearDown(self):
        from application.extensions import db
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_customer_endpoints(self):
        """Test all customer endpoints"""
        endpoints = [
            ('GET', '/customers/', 'Customer list'),
            ('POST', '/customers/login', 'Customer login'),
            ('GET', '/customers/profile', 'Customer profile'),
            ('GET', '/customers/1', 'Specific customer'),
            ('GET', '/customers/my-tickets', 'Customer tickets'),
        ]
        
        print("\n=== Customer Endpoints ===")
        for method, endpoint, description in endpoints:
            response = None
            if method == 'GET':
                response = self.client.get(endpoint)
            elif method == 'POST':
                response = self.client.post(endpoint, json={})
            
            if response:
                print(f"{method} {endpoint} ({description}): {response.status_code}")
        
        print("=== End Customer Endpoints ===\n")
    
    def test_mechanic_endpoints(self):
        """Test all mechanic endpoints"""
        endpoints = [
            ('GET', '/mechanic/', 'Mechanic list'),
            ('POST', '/mechanic/login', 'Mechanic login'),
            ('GET', '/mechanic/profile', 'Mechanic profile'),
            ('GET', '/mechanic/1', 'Specific mechanic'),
        ]
        
        print("\n=== Mechanic Endpoints ===")
        for method, endpoint, description in endpoints:
            response = None
            if method == 'GET':
                response = self.client.get(endpoint)
            elif method == 'POST':
                response = self.client.post(endpoint, json={})
            
            if response:
                print(f"{method} {endpoint} ({description}): {response.status_code}")
        
        print("=== End Mechanic Endpoints ===\n")

if __name__ == '__main__':
    unittest.main()