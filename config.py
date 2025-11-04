import os
from datetime import timedelta
class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:{os.getenv('DB_PASSWORD')}@localhost/Mechanic_shop"
    RATELIMIT_DEFAULT = "100 per day;20 per hour"

    # Cache configuration
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

    # Rate Limiting
    RATELIMIT_STORAGE_URI = 'memory://http://localhost:6379/0'
    
    
    # JWT Settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

class DevelopmentConfig(Config):
    DEBUG = True
    # Ensure SQLite for development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mechanics.db'

class ProductionConfig(Config):
    DEBUG = False
   