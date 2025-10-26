from .extensions import db, bcrypt

service_ticket_mechanic = db.Table(
    'service_ticket_mechanic',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'), primary_key=True)
)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Mechanic(db.Model):
    __tablename__ = 'mechanics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    salary = db.Column(db.Float)
    address = db.Column(db.String(255))
    service_tickets = db.relationship('ServiceTicket', secondary=service_ticket_mechanic, back_populates='mechanics')

class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    total_cost = db.Column(db.Float)
    status = db.Column(db.String(100))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    mechanics = db.relationship('Mechanic', secondary=service_ticket_mechanic, back_populates='service_tickets')
