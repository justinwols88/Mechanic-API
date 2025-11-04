from flask import Blueprint

customer_bp = Blueprint('customer', __name__)

from application.blueprints.customer import routes