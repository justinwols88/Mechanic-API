# migration_setup.py - Complete standalone database setup
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mechanics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'temp-secret-key'

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define ALL your models here (copy from your models.py)
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)

class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    status = db.Column(db.String(20), default='open')
    priority = db.Column(db.String(20), default='normal')
    payment_status = db.Column(db.String(20), default='unpaid')
    payment_date = db.Column(db.Date)
    payment_amount = db.Column(db.Float)
    payment_method = db.Column(db.String(20))
    payment_note = db.Column(db.String(255))

class Mechanic(db.Model):
    __tablename__ = 'mechanics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    specialization = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class ServiceTicketInventory(db.Model):
    __tablename__ = 'service_ticket_inventory'
    service_ticket_id = db.Column(db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), primary_key=True)
    quantity_used = db.Column(db.Integer, nullable=False)

class MechanicServiceTicketAssociation(db.Model):
    __tablename__ = 'mechanic_service_ticket_association'
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), primary_key=True)
    service_ticket_id = db.Column(db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

def setup_database():
    """Create all database tables"""
    with app.app_context():
        # Drop all existing tables and create new ones
        db.drop_all()
        db.create_all()
        
        print("✅ Database tables created successfully!")
        print("📊 Tables created:")
        print("   - customers")
        print("   - inventory") 
        print("   - service_tickets")
        print("   - mechanics")
        print("   - service_ticket_inventory")
        print("   - mechanic_service_ticket_association")
        
        # Create a sample customer for testing
        sample_customer = Customer(
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890",
            address="123 Main St"
        )
        sample_customer.set_password("password123")
        
        db.session.add(sample_customer)
        db.session.commit()
        
        print("✅ Sample customer created:")
        print(f"   - Name: John Doe")
        print(f"   - Email: john@example.com")
        print(f"   - Password: password123")

if __name__ == '__main__':
    setup_database()