# tests/test_base.py
import unittest
import sys
import os
from unittest.mock import patch
from application import create_app, db 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BaseTestCase(unittest.TestCase):
    """Base test class with common setup"""
    
    def setUp(self):
        # Patch Flasgger validation
        self.flasgger_patcher = patch('flasgger.utils.validate')
        self.mock_validate = self.flasgger_patcher.start()
        self.mock_validate.return_value = True
        
                
        # Create app with test configuration
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        # Configure cache for testing to avoid warnings
        self.app.config['CACHE_TYPE'] = 'SimpleCache'
        self.app.config['CACHE_DEFAULT_TIMEOUT'] = 300
        
        self.client = self.app.test_client()

    def tearDown(self):
        self.flasgger_patcher.stop()