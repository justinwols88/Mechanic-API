from flask import Blueprint

inventory_bp = Blueprint('inventory', __name__)

from application.blueprints.inventory import routes