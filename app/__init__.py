from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import importlib  # added import

db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mechanic_shop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    db.init_app(app)
    ma.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app import models
    
    # Robust blueprint importer to tolerate different blueprint variable names
    def _import_blueprint(module_path, candidate_names):
        try:
            mod = importlib.import_module(module_path)
        except Exception as e:
            raise ImportError(f"Could not import module '{module_path}': {e}")
        for name in candidate_names:
            bp = getattr(mod, name, None)
            if bp is not None:
                return bp
        raise ImportError(f"No blueprint found in '{module_path}'. Tried names: {candidate_names}")
    
    # Try common names for the blueprint variables in each module
    customer_bp = _import_blueprint('app.customer.routes', ('customer_bp', 'customers_bp', 'bp', 'customer_blueprint', 'customers_blueprint'))
    mechanic_bp = _import_blueprint('app.mechanic.routes', ('mechanic_bp', 'mechanics_bp', 'bp', 'mechanic_blueprint'))
    service_ticket_bp = _import_blueprint('app.service_ticket.routes', ('service_ticket_bp', 'service_tickets_bp', 'bp', 'service_ticket_blueprint'))
    
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app