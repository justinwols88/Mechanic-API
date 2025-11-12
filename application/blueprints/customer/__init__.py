# app/routes/customers.py
from flask import Blueprint

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/')
def get_customers():
    return "Customers route"
__all__ = ['customers_bp']