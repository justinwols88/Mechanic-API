from flask import Blueprint, request, jsonify
from application.extensions import db, limiter, cache
from application.models import Customer, ServiceTicket
from application.blueprints.customer.customerSchemas import customer_schema, customers_schema, login_schema
from auth.tokens import encode_token, token_required
from . import customer_bp  # Import the blueprint instance
from flask import request, jsonify


# Add debug print
print("✓ Loading customer routes")

@customer_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """
    Customer login
    ---
    tags:
      - Customers
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
              example: customer@example.com
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
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      400:
        description: Validation errors
        schema:
          $ref: '#/definitions/ValidationError'
      401:
        description: Invalid credentials
        schema:
          $ref: '#/definitions/Error'
      429:
        description: Too many requests
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    # Your login implementation
    pass

    try:
        errors = login_schema.validate(request.json)
        if errors:
            return jsonify(errors), 400
        
        data = request.json
        customer = Customer.query.filter_by(email=data['email']).first()
        
        if customer and customer.check_password(data['password']):
            token = encode_token(customer.id)
            return jsonify({'token': token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@customer_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    """
    Get customer's service tickets
    ---
    tags:
      - Customers
    security:
      - BearerAuth: []
    responses:
      200:
        description: Customer tickets retrieved successfully
        schema:
          type: array
          items:
            $ref: '#/definitions/ServiceTicket'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
        return jsonify([ticket.to_dict() for ticket in tickets])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve tickets', 'details': str(e)}), 500

@customer_bp.route('/', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_customers():
    """
    Get all customers with pagination
    ---
    tags:
      - Customers
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        description: Page number for pagination
        default: 1
        example: 1
      - name: per_page
        in: query
        type: integer
        required: false
        description: Number of items per page
        default: 10
        example: 10
    responses:
      200:
        description: Customers retrieved successfully
        schema:
          type: object
          properties:
            customers:
              type: array
              items:
                $ref: '#/definitions/Customer'
            total:
              type: integer
              example: 150
            pages:
              type: integer
              example: 15
            current_page:
              type: integer
              example: 1
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        customers = Customer.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'customers': [customer.to_dict() for customer in customers.items],
            'total': customers.total,
            'pages': customers.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve customers', 'details': str(e)}), 500

@customer_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """
    Get specific customer by ID
    ---
    tags:
      - Customers
    parameters:
      - name: customer_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Customer retrieved successfully
        schema:
          $ref: '#/definitions/Customer'
      404:
        description: Customer not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        customer = Customer.query.get_or_404(customer_id)
        return jsonify(customer_schema.dump(customer))
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve customer', 'details': str(e)}), 500

@customer_bp.route('/', methods=['POST'])
def create_customer():
    """
    Create a new customer
    ---
    tags:
      - Customers
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CustomerRegistration'
    responses:
      201:
        description: Customer created successfully
        schema:
          $ref: '#/definitions/Customer'
      400:
        description: Validation errors
        schema:
          $ref: '#/definitions/ValidationError'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        data = request.json
        errors = customer_schema.validate(data)
        if errors:
            return jsonify(errors), 400
        
        customer = customer_schema.load(data)
        customer.set_password(data['password'])
        
        db.session.add(customer)
        db.session.commit()
        return jsonify(customer_schema.dump(customer)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create customer', 'details': str(e)}), 500

@customer_bp.route('/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(customer_id, token_customer_id):
    """
    Update customer profile
    ---
    tags:
      - Customers
    security:
      - BearerAuth: []
    parameters:
      - name: customer_id
        in: path
        type: integer
        required: true
        example: 1
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CustomerUpdate'
    responses:
      200:
        description: Customer updated successfully
        schema:
          $ref: '#/definitions/Customer'
      400:
        description: Validation errors
        schema:
          $ref: '#/definitions/ValidationError'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      403:
        description: Forbidden - Cannot update other customers
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Customer not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        if customer_id != int(token_customer_id):
            return jsonify({'message': 'Unauthorized'}), 403
            
        customer = Customer.query.get_or_404(customer_id)
        data = request.json
        customer = customer_schema.load(data, instance=customer)
        db.session.commit()
        return jsonify(customer_schema.dump(customer))
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update customer', 'details': str(e)}), 500

@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(customer_id, token_customer_id):
    """
    Delete customer account
    ---
    tags:
      - Customers
    security:
      - BearerAuth: []
    parameters:
      - name: customer_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      204:
        description: Customer deleted successfully
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      403:
        description: Forbidden - Cannot delete other customers
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Customer not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        if customer_id != int(token_customer_id):
            return jsonify({'message': 'Unauthorized'}), 403
            
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete customer', 'details': str(e)}), 500

@customer_bp.route('/profile', methods=['GET'])
@token_required
def get_customer_profile(customer_id):
    """
    Get current customer profile
    ---
    tags:
      - Customers
    security:
      - BearerAuth: []
    responses:
      200:
        description: Customer profile retrieved successfully
        schema:
          $ref: '#/definitions/Customer'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Customer not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        customer = Customer.query.get_or_404(customer_id)
        return jsonify(customer_schema.dump(customer))
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve profile', 'details': str(e)}), 500
    
@customer_bp.route('/my-tickets', methods=['GET'])  # Should be '/my-tickets'
@token_required
def get_my_tickets(customer_id):
    """
    Get customer's service tickets
    """
    try:
        tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
        return jsonify([ticket.to_dict() for ticket in tickets])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve tickets', 'details': str(e)}), 500
