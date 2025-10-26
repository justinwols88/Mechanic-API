from flask import Flask
from config import DevelopmentConfig
from .extensions import db, ma, bcrypt, limiter, cache
from .blueprints.customer import customer_bp
from .blueprints.mechanic import mechanic_bp
from .blueprints.service_ticket import service_ticket_bp

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    app.register_blueprint(customer_bp)
    app.register_blueprint(mechanic_bp)
    app.register_blueprint(service_ticket_bp)
    with app.app_context():
        db.create_all()
    return app
