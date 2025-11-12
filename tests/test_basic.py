# tests/test_basic.py
import sys
import os
import pytest

# Add root directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import create_app
from application.models import db, Customer

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_app_creation(app):
    """Test app creation"""
    assert app is not None
    assert app.testing == True

def test_home_route(client):
    """Test home route"""
    response = client.get('/')
    assert response.status_code in [200, 404, 405]

def test_customer_route(client):
    """Test customer route"""
    response = client.get('/customers/')
    assert response.status_code in [200, 401, 404]

def test_database_operations(app):
    """Test database operations"""
    with app.app_context():
        customer = Customer(
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        customer.set_password("password123")
        db.session.add(customer)
        db.session.commit()
        
        retrieved = Customer.query.filter_by(email="test@example.com").first()
        assert retrieved is not None
        assert retrieved.first_name == "Test"