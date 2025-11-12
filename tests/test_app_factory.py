from application import create_app, db 
import unittest

class TestBase(unittest.TestCase):
    def setUp(self):
        """Set up test client before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up after each test"""
        pass
