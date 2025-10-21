from flask import request, jsonify
from app.Mechanic import mechanic_bp
from app.Mechanic.models import Mechanic
from app.Mechanic.schemas import mechanic_schema, mechanics_schema
from app import db
from app.customer.routes import token_required

@mechanic_bp.route('/', methods=['POST'])
@token_required
def create_mechanic(customer_id):
    """
    Create mechanic - requires authentication
    """
    try:
        data = request.get_json()
        
        errors = mechanic_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400
        
        mechanic = mechanic_schema.load(data)
        db.session.add(mechanic)
        db.session.commit()
        
        return mechanic_schema.jsonify(mechanic), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mechanic_bp.route('/', methods=['GET'])
def get_mechanics():
    """
    Get all mechanics - public access
    """
    try:
        mechanics = Mechanic.query.all()
        return mechanics_schema.jsonify(mechanics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mechanic_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_mechanic(customer_id, id):
    """
    Update mechanic - requires authentication
    """
    try:
        mechanic = Mechanic.query.get_or_404(id)
        data = request.get_json()
        
        errors = mechanic_schema.validate(data, partial=True)
        if errors:
            return jsonify({"errors": errors}), 400
        
        mechanic = mechanic_schema.load(data, instance=mechanic, partial=True)
        db.session.commit()
        
        return mechanic_schema.jsonify(mechanic)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mechanic_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_mechanic(customer_id, id):
    """
    Delete mechanic - requires authentication
    """
    try:
        mechanic = Mechanic.query.get_or_404(id)
        db.session.delete(mechanic)
        db.session.commit()
        
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500