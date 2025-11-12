# tests/test_mechanic_login.py
import pytest
from app import create_app
from application.models import Mechanic, db

@pytest.fixture
def mechanic():
    """Fixture to create a test mechanic"""
    mechanic = Mechanic(
        first_name="Test",
        last_name="Mechanic",
        email="test@example.com",
        phone="555-1234",
        address="123 Test St",
        specialization="General",
        password_hash=None
    )
    mechanic.set_password("password123")
    return mechanic

def test_mechanic_login():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        # Create a test mechanic with CORRECT field names
        mechanic = Mechanic(
            first_name="Test",  # NOT 'name'
            last_name="Mechanic",
            email="test@example.com",
            phone="555-1234"
        )
        mechanic.set_password("password123")
        
        db.session.add(mechanic)
        db.session.commit()
        
        # Test password verification
        assert mechanic.check_password("password123") == True
        assert mechanic.check_password("wrongpassword") == False