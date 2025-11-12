# tests/test_config.py
import os
from tests.test_base import BaseTestCase
from application import create_app, db 

class TestConfig:
    """Configuration for testing environment"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    
    # Disable Flasgger validation in tests
    FLASGGER_VALIDATION = False
    
    # Add any other configuration your app needs