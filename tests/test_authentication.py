# tests/test_authentication.py
import pytest
from app import create_app
from application.models import Customer, Mechanic, db

class TestAuthentication:
    
    # Customer Authentication Tests
    def test_customer_login(self, app):
        """Test customer login functionality"""
        with app.app_context():
            # Create a test customer
            customer = Customer(
                first_name="Test",
                last_name="User", 
                email="test@example.com",
                phone="123-456-7890"
            )
            customer.set_password("password123")
            
            db.session.add(customer)
            db.session.commit()
            
            # Test password verification
            assert customer.check_password("password123") == True
            assert customer.check_password("wrongpassword") == False
            
            # Test to_dict method
            customer_dict = customer.to_dict()
            assert customer_dict['email'] == "test@example.com"
            assert customer_dict['first_name'] == "Test"
    
    def test_customer_registration(self, app):
        """Test customer registration"""
        with app.app_context():
            # Test creating customer without password
            customer = Customer(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone="555-1234"
            )
            
            db.session.add(customer)
            db.session.commit()
            
            assert customer.id is not None
            assert customer.password_hash is None
    
    def test_customer_password_hashing(self, app):
        """Test password hashing functionality"""
        with app.app_context():
            customer = Customer(
                first_name="Password",
                last_name="Test",
                email="password@example.com"
            )
            
            # Test setting and checking password
            customer.set_password("securepassword")
            assert customer.password_hash is not None
            assert customer.password_hash != "securepassword"  # Should be hashed
            assert customer.check_password("securepassword") == True
            assert customer.check_password("wrong") == False

    # Mechanic Authentication Tests
    def test_mechanic_login(self, app):
        """Test mechanic login functionality"""
        with app.app_context():
            # Create a test mechanic
            mechanic = Mechanic(
                first_name="Mechanic",
                last_name="Test", 
                email="mechanic@example.com",
                phone="987-654-3210"
            )
            mechanic.set_password("mechanic123")
            
            db.session.add(mechanic)
            db.session.commit()
            
            # Test password verification
            assert mechanic.check_password("mechanic123") == True
            assert mechanic.check_password("wrongpassword") == False
            
            # Test to_dict method
            mechanic_dict = mechanic.to_dict()
            assert mechanic_dict['email'] == "mechanic@example.com"
            assert mechanic_dict['first_name'] == "Mechanic"
    
    def test_mechanic_registration(self, app):
        """Test mechanic registration"""
        with app.app_context():
            # Test creating mechanic without password
            mechanic = Mechanic(
                first_name="Jane",
                last_name="Smith",
                email="jane@example.com",
                phone="555-5678"
            )
            
            db.session.add(mechanic)
            db.session.commit()
            
            assert mechanic.id is not None
            assert mechanic.password_hash is None
    
    def test_mechanic_password_hashing(self, app):
        """Test mechanic password hashing functionality"""
        with app.app_context():
            mechanic = Mechanic(
                first_name="Tech",
                last_name="Guru",
                email="tech@example.com"
            )
            
            # Test setting and checking password
            mechanic.set_password("securemechanic")
            assert mechanic.password_hash is not None
            assert mechanic.password_hash != "securemechanic"  # Should be hashed
            assert mechanic.check_password("securemechanic") == True
            assert mechanic.check_password("wrong") == False

    # Comparative Tests
    def test_customer_vs_mechanic_passwords(self, app):
        """Test that customer and mechanic passwords are handled independently"""
        with app.app_context():
            # Create both with same password
            customer = Customer(
                first_name="Same",
                last_name="Password",
                email="customer_same@example.com"
            )
            customer.set_password("samepassword123")
            
            mechanic = Mechanic(
                first_name="Same",
                last_name="Password", 
                email="mechanic_same@example.com"
            )
            mechanic.set_password("samepassword123")
            
            db.session.add_all([customer, mechanic])
            db.session.commit()
            
            # Both should validate their own passwords correctly
            assert customer.check_password("samepassword123") == True
            assert mechanic.check_password("samepassword123") == True
            
            # But password hashes should be different (due to salting)
            assert customer.password_hash != mechanic.password_hash
    
    def test_authentication_edge_cases(self, app):
        """Test edge cases for authentication"""
        with app.app_context():
            # Test empty password
            customer = Customer(
                first_name="Empty",
                last_name="Password",
                email="empty@example.com"
            )
            customer.set_password("")
            
            mechanic = Mechanic(
                first_name="Empty",
                last_name="Password",
                email="empty_mech@example.com"
            )
            mechanic.set_password("")
            
            db.session.add_all([customer, mechanic])
            db.session.commit()
            
            assert customer.check_password("") == True
            assert mechanic.check_password("") == True
            
            # Test very long password
            long_password = "a" * 100
            customer2 = Customer(
                first_name="Long",
                last_name="Password",
                email="long@example.com"
            )
            customer2.set_password(long_password)
            
            assert customer2.check_password(long_password) == True

# Standalone function tests (alternative approach)
def test_customer_standalone_login(app):
    """Standalone test for customer login"""
    with app.app_context():
        customer = Customer(
            first_name="Standalone",
            last_name="Customer",
            email="standalone_customer@example.com"
        )
        customer.set_password("test123")
        
        db.session.add(customer)
        db.session.commit()
        
        assert customer.check_password("test123") == True
        assert customer.check_password("wrong") == False

def test_mechanic_standalone_login(app):
    """Standalone test for mechanic login"""
    with app.app_context():
        mechanic = Mechanic(
            first_name="Standalone",
            last_name="Mechanic",
            email="standalone_mechanic@example.com"
        )
        mechanic.set_password("test456")
        
        db.session.add(mechanic)
        db.session.commit()
        
        assert mechanic.check_password("test456") == True
        assert mechanic.check_password("wrong") == False