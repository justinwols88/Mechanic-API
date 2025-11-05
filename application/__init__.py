from flask import Flask
from application.extensions import db, migrate, ma, cache, limiter
def create_app():
    app = Flask(__name__)
    
    # Use Development config for now
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mechanics.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Import and register blueprints
    try:
        from application.blueprints.customer.routes import customer_bp
        from application.blueprints.mechanic.routes import mechanic_bp
        from application.blueprints.service_ticket.routes import service_ticket_bp
        from application.blueprints.inventory.routes import inventory_bp
        

        app.register_blueprint(customer_bp, url_prefix='/customers')
        app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
        app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')
        app.register_blueprint(inventory_bp, url_prefix='/inventory')
        
        
        print("✅ All blueprints registered successfully!")
        
    except Exception as e:
        print(f"❌ Error registering blueprints: {e}")
    
    return app