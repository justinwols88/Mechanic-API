# blueprints/inventory/__init__.py
from flask import Blueprint

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

__all__ = ['inventory_bp']