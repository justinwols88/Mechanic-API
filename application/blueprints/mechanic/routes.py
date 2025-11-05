from flask import Blueprint, request, jsonify
from application.extensions import db
from application.models import Mechanic, service_mechanic
from application.blueprints.mechanic.mechanicSchemas import mechanic_schema, mechanics_schema, login_schema
from auth.tokens import encode_mechanic_token, mechanic_token_required
from sqlalchemy import func, desc

mechanic_bp = Blueprint('mechanic', __name__)

# Mechanic Login
@mechanic_bp.route('/login', methods=['POST'])
def mechanic_login():
    errors = login_schema.validate(request.json)
    if errors:
        return jsonify(errors), 400
    
    data = request.json
    mechanic = Mechanic.query.filter_by(email=data['email']).first()
    
    if mechanic and mechanic.check_password(data['password']):
        token = encode_mechanic_token(mechanic.id)
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Mechanic Leaderboard
@mechanic_bp.route('/leaderboard', methods=['GET'])
def get_mechanics_leaderboard():
    mechanics = Mechanic.query\
        .outerjoin(service_mechanic)\
        .group_by(Mechanic.id)\
        .order_by(desc(func.count(service_mechanic.c.mechanic_id)))\
        .all()
    
    return jsonify([{
        'mechanic': mechanic.to_dict(),
        'ticket_count': len(mechanic.service_tickets)
    } for mechanic in mechanics])

# Other CRUD routes for mechanics
@mechanic_bp.route('/', methods=['GET'])
def get_mechanics():
    mechanics = Mechanic.query.all()
    return jsonify([mechanic.to_dict() for mechanic in mechanics])

@mechanic_bp.route('/<int:mechanic_id>', methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    return jsonify(mechanic.to_dict())

@mechanic_bp.route('/', methods=['POST'])
def create_mechanic():
    data = request.json
    errors = mechanic_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    mechanic = mechanic_schema.load(data)
    mechanic.set_password(data['password'])
    
    db.session.add(mechanic)
    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic)), 201

@mechanic_bp.route('/<int:mechanic_id>', methods=['PUT'])
@mechanic_token_required
def update_mechanic(mechanic_id, token_mechanic_id):
    if mechanic_id != int(token_mechanic_id):
        return jsonify({'message': 'Unauthorized'}), 403
        
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    data = request.json
    mechanic = mechanic_schema.load(data, instance=mechanic)
    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic))

@mechanic_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@mechanic_token_required
def delete_mechanic(mechanic_id, token_mechanic_id):
    if mechanic_id != int(token_mechanic_id):
        return jsonify({'message': 'Unauthorized'}), 403
        
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    db.session.delete(mechanic)
    db.session.commit()
    return '', 204