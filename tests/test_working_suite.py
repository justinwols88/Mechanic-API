"""
Minimal test suite that should definitely work
"""
import pytest

from application.models import Customer
from application import create_app, db  # ✅ Correct

def test_app_creation():
    """Test basic app creation"""
    app = create_app()
    assert app is not None
    print("✓ App creation works")

def test_database_operations(app):
    """Test basic database operations"""
    with app.app_context():
        # Create tables
        db.create_all()
        print("✓ Database tables created")
        
        # Test Customer model
        customer = Customer(
            first_name="Test",
            last_name="User", 
            email="test@example.com"
        )
        customer.set_password("password123")
        
        db.session.add(customer)
        db.session.commit()
        print("✓ Customer creation works")
        
        # Query customer
        saved = Customer.query.filter_by(email="test@example.com").first()
        assert saved is not None
        assert saved.first_name == "Test"
        assert saved.check_password("password123")
        print("✓ Customer query works")
        
        # Clean up
        db.drop_all()
        print("✓ Database cleanup works")

def test_app_config(app):
    """Test app configuration"""
    assert app.config['TESTING'] == True
    assert 'SQLALCHEMY_DATABASE_URI' in app.config
    print("✓ App configuration works")

if __name__ == '__main__':
    # Run as script
    test_app_creation()
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app_config(app)
    with app.app_context():
        test_database_operations(app)
    print("🎉 All basic tests passed!")