from application import create_app, db
import unittest
from application.models import Customer, Mechanic, Inventory, ServiceTicket, TicketPart
from .test_utils import TestUtils

# tests/test_database_models.py
try:
    from .test_utils import TestUtils  # Direct import
except ImportError:
    from .test_utils import TestUtils  # Relative import

from application.models import Customer, Mechanic, Inventory, ServiceTicket, Vehicle
from application.extensions import db
import unittest

class TestDatabaseModels(unittest.TestCase):
    
    def setUp(self):
        """Set up test database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_customer_model(self):
        """Test customer model creation"""
        customer = Customer(
            first_name="John",
            last_name="Doe", 
            email=TestUtils.generate_unique_email()
        )
        customer.set_password("password123")
        db.session.add(customer)
        db.session.commit()
        
        # Test retrieval
        saved_customer = Customer.query.filter_by(email=customer.email).first()
        self.assertIsNotNone(saved_customer)
        self.assertEqual(saved_customer.first_name, "John")
        self.assertTrue(saved_customer.check_password("password123"))

    def test_mechanic_model(self):
        """Test mechanic model creation"""
        mechanic = Mechanic(
            first_name="Jane",
            last_name="Mechanic",
            email=TestUtils.generate_unique_email()
        )
        mechanic.set_password("password123")
        db.session.add(mechanic)
        db.session.commit()
        
        saved_mechanic = Mechanic.query.filter_by(email=mechanic.email).first()
        self.assertIsNotNone(saved_mechanic)
        self.assertEqual(saved_mechanic.first_name, "Jane")
        self.assertTrue(saved_mechanic.check_password("password123"))

    def test_inventory_model(self):
        """Test inventory model creation"""
        inventory = Inventory(
            name="Test Part",
            description="Test description",
            category="Test Category",
            price=10.0,
            quantity_in_stock=5
        )
        db.session.add(inventory)
        db.session.commit()
        
        saved_inventory = Inventory.query.filter_by(name="Test Part").first()
        self.assertIsNotNone(saved_inventory)
        self.assertEqual(saved_inventory.quantity_in_stock, 5)
        self.assertEqual(saved_inventory.price, 10.0)

    def test_service_ticket_model(self):
        """Test service ticket model creation"""
        # First create customer and vehicle
        customer = TestUtils.create_test_customer()
        db.session.add(customer)
        db.session.flush()
        
        vehicle = TestUtils.create_test_vehicle(customer.id)
        db.session.add(vehicle)
        db.session.flush()
        
        # Then create service ticket
        ticket = ServiceTicket(
            customer_id=customer.id,
            vehicle_id=vehicle.id,
            issue_description="Test issue description",
            status="open"
        )
        db.session.add(ticket)
        db.session.commit()
        
        saved_ticket = ServiceTicket.query.filter_by(customer_id=customer.id).first()
        self.assertIsNotNone(saved_ticket)
        self.assertEqual(saved_ticket.issue_description, "Test issue description")
        self.assertEqual(saved_ticket.status, "open")

if __name__ == '__main__':
    unittest.main()