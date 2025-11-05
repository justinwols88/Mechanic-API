import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = False
    TESTING = False
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mechanics.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Cache configuration
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev_mechanics.db'

class ProductionConfig(Config):
    """Production configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}