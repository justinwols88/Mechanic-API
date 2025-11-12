# tests/__init__.py


"""
Centralized imports for all tests to avoid multiple SQLAlchemy instances
"""
from application import create_app, db
from application.models import Customer, Mechanic, Inventory, ServiceTicket, TicketPart

__all__ = [
    'create_app',
    'db',
    'Customer',
    'Mechanic',
    'Inventory',
    'ServiceTicket',
    'TicketPart'
]