# application/blueprints/vehicles/__init__.py
"""
Vehicles Blueprint Package
"""

from flask import Blueprint

# Create the vehicles blueprint
vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

__all__ = ['vehicles_bp']