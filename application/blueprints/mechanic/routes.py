from flask import Blueprint, request, jsonify
from application.extensions import db, limiter, cache
from application.models import Mechanic, ServiceTicket
from application.blueprints.mechanic import mechanicSchemas
from application.blueprints.mechanic.mechanicSchemas import mechanic_schema, mechanics_schema, login_schema
from application.utils.jwt import encode_token, token_required
import bcrypt

mechanic_bp = Blueprint('mechanic', __name__)

# Top mechanics by ticket count
@mechanic_bp.route('/top', methods=["GET"])
def top_mechanics():
    """Get top mechanics by number of service tickets"""
    mechanics = db.session.query(
        Mechanic, func.count(ServiceTicket.id).label("ticket_count")
    ).join(Mechanic.service_ticket_associations).group_by(Mechanic.id).order_by(func.count(ServiceTicket.id).desc()).limit(10).all()

    result = [{
        "mechanic": mechanic_schema.dump(mechanic),
        "ticket_count": ticket_count
    } for mechanic, ticket_count in mechanics]

    return jsonify(result)

# Example cached route
@cache.cached(timeout=60, key_prefix='mechanics_list')
@mechanic_bp.route('/cached', methods=['GET'])
def cached_route():
    """Get mechanics with caching"""
    mechanics = Mechanic.query.all()
    return jsonify(mechanic_schema.dump(mechanics))

# Example rate-limited route
@limiter.limit("10 per minute")
@mechanic_bp.route('/rate-limited', methods=['GET'])
def rate_limited_route():
    return jsonify({"message": "This route is rate limited"})

# Get all mechanics
@mechanic_bp.route('/', methods=['GET'])
@token_required
def get_mechanics():
    """Get all mechanics"""
    mechanics = Mechanic.query.all()
    return jsonify(mechanics_schema.dump(mechanics))

# Register new mechanic
@mechanic_bp.route('/register', methods=['POST'])
def register_mechanic():
    data = request.get_json()

    # Validate incoming data
    errors = mechanic_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    if Mechanic.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Hash password securely
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_mechanic = Mechanic(
        name=data.get('name'),
        email=email,
        phone=data.get('phone'),
        address=data.get('address'),
        specialization=data.get('specialization'),
        password_hash=hashed_password
    )

    try:
        db.session.add(new_mechanic)
        db.session.commit()
        cache.delete('mechanics_list')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to register mechanic', 'details': str(e)}), 500

    return jsonify(mechanic_schema.dump(new_mechanic)), 201
@mechanic_bp.route('/login', methods=["POST"])
def login():
    """Mechanic login"""
    data = request.get_json()
    
    # Validate input
    errors = login_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Find mechanic by email
    mechanic = Mechanic.query.filter_by(email=data.get('email')).first()
    
    # Check if mechanic exists and password is correct
    if mechanic and mechanic.check_password(data.get('password')):
        token = encode_token(mechanic.id, "mechanic")
        return jsonify({
            "token": token,
            "mechanic": mechanic_schema.dump(mechanic)
        })
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Get mechanic profile
@mechanic_bp.route('/profile', methods=['GET'])
@token_required
def get_mechanic_profile():
    """Get current mechanic profile"""
    mechanic_id = getattr(request, 'user_id', None)
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    return jsonify(mechanic_schema.dump(mechanic))

# Update mechanic profile
@mechanic_bp.route('/profile', methods=['PUT'])
@token_required
def update_mechanic_profile():
    """Update current mechanic profile"""
    mechanic_id = getattr(request, 'user_id', None)
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    data = request.get_json()
    
    # Validate input
    errors = mechanic_schema.validate(data, partial=True)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Update fields
    if 'name' in data:
        mechanic.name = data['name']
    if 'phone' in data:
        mechanic.phone = data['phone']
    if 'address' in data:
        mechanic.address = data['address']
    if 'specialization' in data:
        mechanic.specialization = data['specialization']
    if 'password' in data:
        mechanic.set_password(data['password'])
    
    try:
        db.session.commit()
        cache.delete('mechanics_list')  # Clear cache
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500
    
    return jsonify(mechanic_schema.dump(mechanic))

# Get specific mechanic
@mechanic_bp.route('/<int:mechanic_id>', methods=['GET'])
@token_required
def get_mechanic(mechanic_id):
    """Get a specific mechanic"""
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    return jsonify(mechanic_schema.dump(mechanic))

# Update specific mechanic (admin function)
@mechanic_bp.route('/<int:mechanic_id>', methods=['PUT'])
@token_required
def update_mechanic(mechanic_id):
    """Update a specific mechanic (admin function)"""
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    data = request.get_json()
    
    # Validate input
    errors = mechanic_schema.validate(data, partial=True)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Update fields
    updatable_fields = ['name', 'email', 'phone', 'address', 'specialization']
    for field in updatable_fields:
        if field in data:
            setattr(mechanic, field, data[field])
    
    if 'password' in data:
        mechanic.set_password(data['password'])
    
    try:
        db.session.commit()
        cache.delete('mechanics_list')  # Clear cache
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update mechanic', 'details': str(e)}), 500
    
    return jsonify(mechanic_schema.dump(mechanic))

# Delete mechanic
@mechanic_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@token_required
def delete_mechanic(mechanic_id):
    """Delete a mechanic"""
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    
    try:
        db.session.delete(mechanic)
        db.session.commit()
        cache.delete('mechanics_list')  # Clear cache
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete mechanic', 'details': str(e)}), 500
    
    return jsonify({'message': 'Mechanic deleted successfully'}), 200
