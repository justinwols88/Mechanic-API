from application.models import Inventory
import pytest
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import create_app, db, cache

@pytest.fixture(scope='function')
def app():
    """Create application for testing with proper cache initialization"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'CACHE_TYPE': 'SimpleCache',  # ✅ Use SimpleCache for testing
        'CACHE_DEFAULT_TIMEOUT': 300,
    })
    
    # ✅ Explicitly initialize cache with app context
    with app.app_context():
        cache.init_app(app)  # This ensures cache has the app reference
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@staticmethod
def create_test_inventory():
    """Create test inventory items"""
    items = []
        
    # Create multiple inventory items
    inventory1 = Inventory(
        name="Engine Oil",
        description="Synthetic engine oil 5W-30",
        category="Lubricants",
        price=29.99,
        quantity_in_stock=50
    )
    db.session.add(inventory1)
    items.append(inventory1)
        
    inventory2 = Inventory(
        name="Brake Pads",
        description="Premium brake pads set",
        category="Brakes", 
        price=89.99,
        quantity_in_stock=25
    )
    db.session.add(inventory2)
    items.append(inventory2)
        
    inventory3 = Inventory(
        name="Air Filter",
        description="High-performance air filter",
        category="Filters",
        price=24.99,
        quantity_in_stock=10  # Low stock for testing
    )
    db.session.add(inventory3)
    items.append(inventory3)
        
    db.session.commit()
    return items