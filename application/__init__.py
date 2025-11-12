import os
from flask import Flask
from .extensions import db, migrate, jwt, cors, limiter, cache, ma
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from config import Config, TestConfig


def create_app(config_class=None):
    app = Flask(__name__)

    # Use TestConfig for testing if no config provided
    if config_class is None:
        if os.environ.get('TESTING') or os.environ.get('FLASK_ENV') == 'testing':
            config_class = TestConfig
        else:
            config_class = Config# Use TestConfig for testing if no config provided
    
    # Use test config for tests, otherwise use default config
    app.config.from_object('config.Config')
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    ma.init_app(app)
    
    # Import models (important for migrations and relationships)
    from application.models import Customer, Mechanic, Inventory, ServiceTicket, TicketPart, Vehicle
    
    # Import and register blueprints
    from .blueprints.customer.routes import customer_bp
    from .blueprints.mechanic.routes import mechanic_bp
    from .blueprints.inventory.routes import inventory_bp
    from .blueprints.service_ticket.routes import service_ticket_bp
    from .blueprints.vehicles.routes import vehicles_bp
    
    # Register blueprints
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(mechanic_bp, url_prefix='/mechanic')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')

    
    # Print loaded routes for debugging
    print("✓ Customer routes loaded")
    print("✓ Mechanic routes loaded")
    print("✓ Inventory routes loaded")
    print("✓ Vehicle routes loaded")
    print("✓ Service Ticket routes loaded")
    
    return app