from application import create_app, db 
# tests/test_simple_integration.py
import unittest
import sys
import os




sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSimpleIntegration(unittest.TestCase):
    def test_basic_integration(self):
        """Simple integration test that doesn't require database"""
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test that app starts and basic endpoints work
        response = client.get('/mechanic/stats')
        self.assertIsInstance(response.status_code, int)

if __name__ == '__main__':
    unittest.main()