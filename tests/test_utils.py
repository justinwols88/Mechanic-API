# tests/test_utils.py
import random
import string
from application import db
from application.models import Mechanic, Customer, Inventory, ServiceTicket, Vehicle

class TestUtils:
    _email_counter = 0  # Class variable to ensure unique emails
    
    @classmethod
    def _generate_unique_email(cls):
        """Generate a unique email for testing"""
        cls._email_counter += 1
        return f"test_{cls._email_counter}_{random.randint(1000, 9999)}@example.com"

    @staticmethod
    def create_test_customer():
        """Create a test customer"""
        from application.models import Customer
        customer = Customer(
            first_name="Test",
            last_name="Customer", 
            email=TestUtils._generate_unique_email()
        )
        customer.set_password("password123")
        return customer

    @staticmethod
    def create_test_mechanic():
        """Create a test mechanic"""
        from application.models import Mechanic
        mechanic = Mechanic(
            first_name="Test",
            last_name="Mechanic",
            email=TestUtils._generate_unique_email()
        )
        mechanic.set_password("password123")
        return mechanic

    @staticmethod
    def create_test_inventory():
        """Create test inventory items"""
        from application.models import Inventory
        items = [
            Inventory(
                name="Engine Oil",
                description="Synthetic engine oil 5W-30",
                category="Lubricants",
                price=29.99,
                quantity_in_stock=50
            ),
            Inventory(
                name="Air Filter",
                description="Premium air filter",
                category="Filters", 
                price=15.99,
                quantity_in_stock=25
            ),
            Inventory(
                name="Brake Pads",
                description="Ceramic brake pads",
                category="Brakes",
                price=45.99,
                quantity_in_stock=15
            )
        ]
        return items

    @staticmethod
    def create_test_service_ticket(customer_id, vehicle_id):
        """Create a test service ticket"""
        from application.models import ServiceTicket
        ticket = ServiceTicket(
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            issue_description="Test issue description",
            status="open"
        )
        return ticket

    @staticmethod
    def create_test_vehicle(customer_id):
        """Create a test vehicle"""
        from application.models import Vehicle
        vehicle = Vehicle(
            customer_id=customer_id,
            make="Toyota",
            model="Camry", 
            year=2020,
            vin="".join(random.choices(string.ascii_uppercase + string.digits, k=17))
        )
        return vehicle

    @staticmethod
    def generate_unique_email():
        """Generate a unique email for testing"""
        return TestUtils._generate_unique_email()

    @staticmethod
    def get_auth_headers(token):
        """Get authorization headers for authenticated requests"""
        return {'Authorization': f'Bearer {token}'}

    @staticmethod
    def cleanup_test_data():
        """Clean up all test data from the database"""
        from application.models import ServiceTicketMechanic, TicketPart, ServiceTicket, Vehicle, Inventory, Mechanic, Customer
        try:
            db.session.query(ServiceTicketMechanic).delete()
            db.session.query(TicketPart).delete()
            db.session.query(ServiceTicket).delete()
            db.session.query(Vehicle).delete()
            db.session.query(Inventory).delete()
            db.session.query(Mechanic).delete()
            db.session.query(Customer).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Cleanup error: {e}")

    @staticmethod
    def cleanup_all_data():
        """Clean up all test data from database"""
        db.session.query(Mechanic).delete()
        db.session.commit()