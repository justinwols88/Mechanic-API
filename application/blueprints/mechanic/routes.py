from flask import request, jsonify
from application.extensions import db, cache, limiter
from application.models import Mechanic
from application.blueprints.mechanic.mechanicSchemas import mechanic_schema, mechanics_schema, login_schema
from auth.tokens import encode_token, token_required
from . import mechanic_bp

@mechanic_bp.route('/stats', methods=['GET'])
def mechanic_stats():
    """
    Get mechanics with ticket counts
    ---
    tags:
      - Mechanics
    responses:
      200:
        description: Statistics retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              mechanic:
                $ref: '#/definitions/MechanicResponse'
              ticket_count:
                type: integer
                example: 5
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        mechanics = db.session.query(
            Mechanic, 
            db.func.count(Mechanic.service_tickets).label('ticket_count')
        ).outerjoin(Mechanic.service_tickets).group_by(Mechanic.id).all()
        
        result = [{
            "mechanic": mechanic_schema.dump(mechanic),
            "ticket_count": ticket_count,
        } for mechanic, ticket_count in mechanics]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve statistics', 'details': str(e)}), 500

@mechanic_bp.route('/cached', methods=['GET'])
@cache.cached(timeout=60, key_prefix='mechanics_list')
def cached_route():
    """
    Get cached mechanics list
    ---
    tags:
      - Mechanics
    responses:
      200:
        description: Mechanics retrieved successfully from cache
        schema:
          type: array
          items:
            $ref: '#/definitions/MechanicResponse'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        mechanics = Mechanic.query.all()
        return jsonify(mechanics_schema.dump(mechanics))
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve cached mechanics', 'details': str(e)}), 500

@mechanic_bp.route('/rate-limited', methods=['GET'])
@limiter.limit("10 per minute")
def rate_limited_route():
    """
    Rate limited test endpoint
    ---
    tags:
      - Mechanics
    responses:
      200:
        description: Request successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: "This route is rate limited"
      429:
        description: Too many requests
        schema:
          $ref: '#/definitions/Error'
    """
    return jsonify({"message": "This route is rate limited"})

@mechanic_bp.route('/', methods=['GET'])
@token_required
def get_mechanics():
    """
    Get all mechanics
    ---
    tags:
      - Mechanics
    security:
      - BearerAuth: []
    responses:
      200:
        description: Mechanics retrieved successfully
        schema:
          type: array
          items:
            $ref: '#/definitions/MechanicResponse'
      401:
        description: Unauthorized - Token missing or invalid
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        mechanics = Mechanic.query.all()
        return jsonify(mechanics_schema.dump(mechanics))
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve mechanics', 'details': str(e)}), 500

@mechanic_bp.route('/register', methods=['POST'])
def register_mechanic():
    """
    Register a new mechanic
    ---
    tags:
      - Mechanics
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicRegistration'
    responses:
      201:
        description: Mechanic registered successfully
        schema:
          $ref: '#/definitions/MechanicResponse'
      400:
        description: Missing required fields
        schema:
          $ref: '#/definitions/Error'
      409:
        description: Email already registered
        schema:
          $ref: '#/definitions/Error'
      422:
        description: Validation errors
        schema:
          $ref: '#/definitions/ValidationError'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        data = request.get_json()
        
        # Validate data
        errors = mechanic_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if mechanic exists
        existing_mechanic = Mechanic.query.filter_by(email=email).first()
        if existing_mechanic:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new mechanic
        new_mechanic = Mechanic(
            name=data.get('name'),
            email=email,
            phone=data.get('phone'),
            address=data.get('address'),
            specialization=data.get('specialization')
        )
        
        # Set password
        new_mechanic.set_password(password)
        
        db.session.add(new_mechanic)
        db.session.commit()
        cache.delete('mechanics_list')
        
        return jsonify({
            'message': 'Mechanic registered successfully',
            'mechanic': mechanic_schema.dump(new_mechanic)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to register mechanic', 'details': str(e)}), 500

@mechanic_bp.route('/login', methods=['POST'])
def login():
    """
    Mechanic login
    ---
    tags:
      - Mechanics
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: mechanic@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            token:
              type: string
            mechanic:
              $ref: '#/definitions/MechanicResponse'
      400:
        description: Validation errors
        schema:
          $ref: '#/definitions/ValidationError'
      401:
        description: Invalid credentials
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        data = request.get_json()
        errors = login_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        mechanic = Mechanic.query.filter_by(email=data.get('email')).first()
        
        if mechanic and mechanic.check_password(data.get('password')):
            token = encode_token(mechanic.id, "mechanic")
            return jsonify({
                "token": token,
                "mechanic": mechanic_schema.dump(mechanic)
            })
        
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@mechanic_bp.route('/profile', methods=['GET'])
@token_required
def mechanic_profile():
    """
    Get current mechanic profile
    ---
    tags:
      - Mechanics
    security:
      - BearerAuth: []
    responses:
      200:
        description: Profile retrieved successfully
        schema:
          $ref: '#/definitions/MechanicResponse'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Mechanic not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        mechanic_id = getattr(request, 'user_id', None)
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        return jsonify(mechanic_schema.dump(mechanic))
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve profile', 'details': str(e)}), 500

@mechanic_bp.route('/profile', methods=['PUT'])
@token_required
def update_mechanic_profile():
    """
    Update current mechanic profile
    ---
    tags:
      - Mechanics
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicUpdate'
    responses:
      200:
        description: Profile updated successfully
        schema:
          $ref: '#/definitions/MechanicResponse'
      400:
        description: Validation errors
        schema:
          $ref: '#/definitions/ValidationError'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Mechanic not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        data = request.get_json()
        mechanic_id = getattr(request, 'user_id', None)
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        errors = mechanic_schema.validate(data, partial=True)
        if errors:
            return jsonify({'errors': errors}), 400
        
        for field in ['name', 'phone', 'address', 'specialization']:
            if field in data:
                setattr(mechanic, field, data[field])
        
        if 'password' in data:
            mechanic.set_password(data['password'])
        
        db.session.commit()
        cache.delete('mechanics_list')
        return jsonify(mechanic_schema.dump(mechanic))
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

@mechanic_bp.route('/<int:mechanic_id>', methods=['GET'])
@token_required
def get_mechanic(mechanic_id):
    """
    Get specific mechanic by ID
    ---
    tags:
      - Mechanics
    security:
      - BearerAuth: []
    parameters:
      - name: mechanic_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Mechanic retrieved successfully
        schema:
          $ref: '#/definitions/MechanicResponse'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Mechanic not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        return jsonify(mechanic_schema.dump(mechanic))
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve mechanic', 'details': str(e)}), 500

@mechanic_bp.route('/<int:mechanic_id>', methods=['PUT'])
@token_required
def update_mechanic(mechanic_id):
    """
    Update specific mechanic by ID
    ---
    tags:
      - Mechanics
    security:
      - BearerAuth: []
    parameters:
      - name: mechanic_id
        in: path
        type: integer
        required: true
        example: 1
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicUpdate'
    responses:
      200:
        description: Mechanic updated successfully
        schema:
          $ref: '#/definitions/MechanicResponse'
      400:
        description: Validation errors
        schema:
          $ref: '#/definitions/ValidationError'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Mechanic not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        data = request.get_json()
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        errors = mechanic_schema.validate(data, partial=True)
        if errors:
            return jsonify({'errors': errors}), 400
        
        updatable_fields = ['name', 'email', 'phone', 'address', 'specialization']
        for field in updatable_fields:
            if field in data:
                setattr(mechanic, field, data[field])
        
        if 'password' in data:
            mechanic.set_password(data['password'])
        
        db.session.commit()
        cache.delete('mechanics_list')
        return jsonify(mechanic_schema.dump(mechanic))
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update mechanic', 'details': str(e)}), 500

@mechanic_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@token_required
def delete_mechanic(mechanic_id):
    """
    Delete specific mechanic by ID
    ---
    tags:
      - Mechanics
    security:
      - BearerAuth: []
    parameters:
      - name: mechanic_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Mechanic deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Mechanic deleted successfully"
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Mechanic not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        db.session.delete(mechanic)
        db.session.commit()
        cache.delete('mechanics_list')
        return jsonify({'message': 'Mechanic deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete mechanic', 'details': str(e)}), 500
    
# Add this to one of your blueprints, e.g., in mechanic/routes.py
@mechanic_bp.route('/cache-test')
@cache.cached(timeout=60)
def cache_test():
    import time
    current_time = time.time()
    return jsonify({
        'message': 'This response is cached for 60 seconds',
        'current_time': current_time,
        'cached_at': current_time
    })