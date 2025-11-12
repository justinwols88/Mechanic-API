# Create a test to debug routes
# tests/test_route_debug.py
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import create_app

class TestRouteDebug(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_list_routes(self):
        """List all registered routes"""
        print("\n=== Registered Routes ===")
        for rule in self.app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule} {list(rule.methods or set())}")
        print("=== End Routes ===\n")
    
    def test_customer_routes(self):
        """Test customer endpoints"""
        endpoints = [
            '/customers/',
            '/customers/login', 
            '/customers/',
            '/customers/1',
            '/customers/profile'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            print(f"{endpoint}: {response.status_code}")

if __name__ == '__main__':
    unittest.main()