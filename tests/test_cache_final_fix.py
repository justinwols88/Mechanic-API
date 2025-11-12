# tests/test_cache_final_fix.py
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import create_app
from tests.test_utils import TestUtils


class TestCacheFinalFix(unittest.TestCase):
    
    def test_customer_list_cache_issue(self):
        """Test customer list endpoint to identify cache issue"""
        app = create_app()
        client = app.test_client()
        
        with app.app_context():
            from application.extensions import db, cache
            db.create_all()
            
            # Create test customer
            customer = TestUtils.create_test_customer()
            
            # Test customer list endpoint
            response = client.get('/customers/')
            print(f"Customer list status: {response.status_code}")
            
            if response.status_code == 500:
                error_data = response.get_json()
                print(f"500 Error details: {error_data}")
                
                # Let's check if it's a cache issue
                print(f"Cache type: {app.config.get('CACHE_TYPE')}")
                print(f"Testing mode: {app.config.get('TESTING')}")
                
                # Try to access cache directly
                try:
                    cache.set('test_key', 'test_value')
                    test_value = cache.get('test_key')
                    print(f"Cache test: {test_value}")
                except Exception as e:
                    print(f"Cache error: {e}")
            
            # Cleanup
            db.session.remove()
            db.drop_all()

if __name__ == '__main__':
    unittest.main()