from email.mime import application
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_marshmallow import Marshmallow
import redis
import os 
# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
cache = Cache()

# Initialize limiter with default limits
limiter = Limiter(
    key_func=get_remote_address, 
    default_limits=["200 per day", "50 per hour"]
)

