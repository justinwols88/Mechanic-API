from flask import Blueprint

mechanic_bp = Blueprint('mechanic', __name__)

from application.blueprints.mechanic import routes