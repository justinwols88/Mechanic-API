from application.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Association tables
service_mechanic = db.Table('service_mechanic',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'), primary_key=True),
    db.Column('assigned_date', db.DateTime, default=datetime.utcnow)
)

service_inventory = db.Table('service_inventory',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'), primary_key=True),
    db.Column('quantity', db.Integer, default=1)
)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    
    # Relationships
    service_tickets = db.relationship('ServiceTicket', backref='customer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address
        }

class Mechanic(db.Model):
    __tablename__ = 'mechanics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    specialization = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))
    
    # Relationships
    service_tickets = db.relationship('ServiceTicket', secondary=service_mechanic, backref='mechanics')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'specialization': self.specialization
        }

class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    status = db.Column(db.String(20), default='open')
    priority = db.Column(db.String(20), default='normal')
    payment_status = db.Column(db.String(20), default='unpaid')
    payment_date = db.Column(db.Date)
    payment_amount = db.Column(db.Float)
    payment_method = db.Column(db.String(20))
    payment_note = db.Column(db.String(255))
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'customer_id': self.customer_id,
            'status': self.status,
            'priority': self.priority
        }

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'description': self.description
        }