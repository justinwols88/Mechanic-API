from flask import Flask
from dotenv import load_dotenv
from flasgger import Swagger
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    from config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    from application.extensions import db, migrate, ma, cache, limiter
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cache.init_app(app)
    
    # Register blueprints
    with app.app_context():
        register_blueprints(app)
    
    # Initialize rate limiter
    limiter.init_app(app)
    
    # Initialize Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "title": "Mechanic API Documentation",
        "uiversion": 3
    }
    
    Swagger(app, config=swagger_config, parse=True)
    
    # DEBUG: Print all registered routes
    print("\n=== REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule.rule} -> {rule.endpoint}")
    print("=== END REGISTERED ROUTES ===\n")
    
    return app  # ← MAKE SURE THIS LINE EXISTS!

def register_blueprints(app):
    """Register all blueprints"""
    from application.blueprints.customer import customer_bp
    from application.blueprints.inventory import inventory_bp
    from application.blueprints.service_ticket import service_ticket_bp
    from application.blueprints.mechanic import mechanic_bp
    
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')
    app.register_blueprint(mechanic_bp, url_prefix='/mechanic')
    
    print("✓ All blueprints registered:")
    print("  - Customers: /customers")
    print("  - Inventory: /inventory") 
    print("  - Service Tickets: /service-tickets")
    print("  - Mechanics: /mechanic")