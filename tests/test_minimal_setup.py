import pytest
from application import create_app, db
from application.models import Customer

def test_app_creation():
    """Test that app can be created without errors"""
    app = create_app()
    assert app is not None

def test_db_initialization(app):
    """Test that database can be initialized"""
    with app.app_context():
        # This should work without errors
        db.create_all()
        
        # Verify we can use the database
        count = Customer.query.count()
        assert count >= 0  # Should not raise exception
        
        db.drop_all()