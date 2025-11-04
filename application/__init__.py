from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    from config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    from application.extensions import db, migrate, ma, limiter, cache
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints (lazy import to avoid circular imports)
    with app.app_context():
        register_blueprints(app)
    
    return app

def register_blueprints(app):
    """Register blueprints - called within app context"""
    from application.blueprints.customer import customer_bp
    from application.blueprints.inventory import inventory_bp
    from application.blueprints.service_ticket import service_ticket_bp
    from application.blueprints.mechanic import mechanic_bp
    
    app.register_blueprint(customer_bp, url_prefix='/api')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(service_ticket_bp, url_prefix='/api/service-tickets')
    app.register_blueprint(mechanic_bp, url_prefix='/api/mechanics')