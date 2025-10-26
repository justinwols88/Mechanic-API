from flask import Blueprint, request, jsonify
from ...extensions import db, limiter
from ...models import Mechanic
from .mechanicSchemas import mechanic_schema, mechanics_schema

mechanic_bp = Blueprint('mechanic_bp', __name__, url_prefix='/mechanics')

@mechanic_bp.route('/', methods=['POST'])
@limiter.limit("5 per minute")
def add_mechanic():
    data = request.get_json()
    mechanic = Mechanic(**data)
    db.session.add(mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 201

@mechanic_bp.route('/', methods=['GET'])
def get_mechanics():
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200
