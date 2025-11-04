from datetime import datetime
from marshmallow import fields
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from application.extensions import db, ma


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))  # Store hashed password
    
    # Relationships
    service_tickets = db.relationship('ServiceTicket', backref='customer', lazy=True)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)
    
    # Relationships
    service_ticket_associations = db.relationship('ServiceTicketInventory', back_populates='inventory_item')

class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)  # Fixed: 'customers.id'
    status = db.Column(db.String(20), default='open')
    priority = db.Column(db.String(20), default='normal')
    payment_status = db.Column(db.String(20), default='unpaid')
    payment_date = db.Column(db.Date)
    payment_amount = db.Column(db.Float)
    payment_method = db.Column(db.String(20))
    payment_note = db.Column(db.String(255))
    
    # Relationships
    inventory_associations = db.relationship('ServiceTicketInventory', back_populates='service_ticket')
    mechanic_associations = db.relationship('MechanicServiceTicketAssociation', back_populates='service_ticket')

class Mechanic(db.Model):
    __tablename__ = 'mechanics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    specialization = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))  # Store hashed password

    # Relationships
    service_ticket_associations = db.relationship('MechanicServiceTicketAssociation', back_populates='mechanic')

    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
# In application/models.py
class ServiceTicketInventory(db.Model):
    __tablename__ = 'service_ticket_inventory'
    
    service_ticket_id = db.Column(db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), primary_key=True)
    quantity_used = db.Column(db.Integer, nullable=False, default=1)  # Quantity field
    
    # Relationships
    service_ticket = db.relationship('ServiceTicket', back_populates='inventory_associations')
    inventory_item = db.relationship('Inventory', back_populates='service_ticket_associations')
class MechanicServiceTicketAssociation(db.Model):
    __tablename__ = 'mechanic_service_ticket_association'
    
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), primary_key=True)
    service_ticket_id = db.Column(db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    removed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships - FIXED: removed extra comma and parenthesis
    mechanic = db.relationship('Mechanic', back_populates='service_ticket_associations')
    service_ticket = db.relationship('ServiceTicket', back_populates='mechanic_associations')

# SCHEMAS - Defined after all models
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True

class ServiceTicketInventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicketInventory
        load_instance = True

class MechanicServiceTicketAssociationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MechanicServiceTicketAssociation
        load_instance = True
        include_fk = True
        fields = ('id','service_ticket_id','inventory_id','quantity_used')
        exclude = ('created_at', 'updated_at','removed_at')
        
class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True
        

# Initialize schemas
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
Mechanic_Schema = MechanicSchema()
mechanic_schemas = MechanicSchema(many=True)
inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
service_ticket_inventory_schema = ServiceTicketInventorySchema()
service_ticket_inventories_schema = ServiceTicketInventorySchema(many=True)
