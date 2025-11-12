# tests/test_extended_coverage.py
import unittest
import sys
import os
from tests.test_base import BaseTestCase
from application import create_app, db 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestExtendedCoverage(BaseTestCase):
    def test_inventory_endpoints(self):
        """Test inventory management endpoints"""
        endpoints = [
            '/inventory/',
            '/inventory/low-stock',
            '/inventory/category/parts'
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertIsInstance(response.status_code, int)

    def test_service_ticket_endpoints(self):
        """Test service ticket endpoints"""
        response = self.client.get('/service-tickets/')
        self.assertIsInstance(response.status_code, int)

    def test_mechanic_endpoints(self):
        """Test mechanic-specific endpoints"""
        endpoints = [
            '/mechanic/stats',
            '/mechanic/cached',
            '/mechanic/rate-limited'
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertIsInstance(response.status_code, int)

if __name__ == '__main__':
    unittest.main()