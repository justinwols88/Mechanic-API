"""
Simple test that should definitely work
"""
import pytest
from application.models import Customer
from application import create_app, db

def test_simple_database_operation(app):
    """Test that we can create and query a customer"""
    with app.app_context():
        # Create a customer
        customer = Customer(
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        customer.set_password("password123")
        
        db.session.add(customer)
        db.session.commit()
        
        # Query the customer
        saved_customer = Customer.query.filter_by(email="john@example.com").first()
        assert saved_customer is not None
        assert saved_customer.first_name == "John"
        assert saved_customer.check_password("password123")

def test_app_exists(app):
    """Test that the app exists"""
    assert app is not None
    assert app.config['TESTING'] == True

def test_database_tables_exist(app):
    """Test that database tables are created"""
    with app.app_context():
        # This will fail if tables don't exist
        customers = Customer.query.all()
        assert isinstance(customers, list)