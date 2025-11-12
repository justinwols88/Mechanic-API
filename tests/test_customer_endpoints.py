import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import create_app, db, cache

class TestCustomerEndpoints(unittest.TestCase):
    
    def setUp(self):
        """Set up test database with proper cache initialization"""
        self.db_fd, self.db_path = tempfile.mkstemp()

        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.db_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'CACHE_TYPE': 'SimpleCache',  # ✅ Add cache config
        })
        
        self.client = self.app.test_client()

        # Create application context and database
        self.app_context = self.app.app_context()
        self.app_context.push()
        cache.init_app(self.app)
        
        db.create_all()
    
    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_customers_list(self):
        """Test getting customers list"""
        response = self.client.get('/customers/')
        self.assertIn(response.status_code, [200, 401])
    
    def test_customer_profile(self):
        """Test getting customer profile"""
        response = self.client.get('/customers/profile')
        self.assertIn(response.status_code, [200, 401])

