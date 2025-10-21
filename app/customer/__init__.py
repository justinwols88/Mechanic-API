from flask import Blueprint

# Define and export the blueprint so "from app.customer import customer_bp" works
customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

# Ensure routes are registered on the blueprint
from . import routes  # noqa: E402,F401

# Explicitly export the symbol
__all__ = ['customer_bp']
