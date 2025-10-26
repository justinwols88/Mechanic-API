class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Jmw602812!!1@localhost/mechanic_shop'
    SECRET_KEY = '123456789abcdef'

class DevelopmentConfig(Config):
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60
