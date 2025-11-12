# application/blueprints/customer/routes.py
from application.models import Customer, ServiceTicket, db, Vehicle, TicketPart
from application.extensions import db, cache
from flask import Blueprint
from flask import request, jsonify
from marshmallow import fields
from application.blueprints.customer.customerSchemas import customer_schema, customers_schema, login_schema
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from auth.tokens import mechanic_token_required, token_required, encode_token

# Create the Blueprint instance
customer_bp = Blueprint('customer', __name__)
limiter = Limiter(key_func=get_remote_address)
from flask_caching import Cache
cache = Cache()
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
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        errors = login_schema.validate(data)
        if errors:
            return jsonify(errors), 400
        
        customer = Customer.query.filter_by(email=data['email']).first()
        
        if customer and customer.check_password(data['password']):
            token = encode_token(customer.id)
            return jsonify({'token': token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500
    
@customer_bp.route('/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(current_customer_id, customer_id):
    """
    Update customer profile
    """
    try:
        # Check authorization - current_customer_id comes from token
        if int(current_customer_id) != customer_id:
            return jsonify({'message': 'Unauthorized - can only update your own profile'}), 403
            
        customer = Customer.query.get_or_404(customer_id)
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Update fields
        if 'first_name' in data:
            customer.first_name = data['first_name']
        if 'last_name' in data:
            customer.last_name = data['last_name']
        if 'email' in data:
            customer.email = data['email']
        if 'phone' in data:
            customer.phone = data['phone']
        if 'address' in data:
            customer.address = data['address']
        
        db.session.commit()
        return jsonify(customer.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update customer', 'details': str(e)}), 500

@customer_bp.route('/', methods=['GET'])
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
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate data against schema
        errors = customer_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Use the validated data directly
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone', ''),
            address=data.get('address', '')
        )
        
        # Set password
        customer.set_password(data['password'])
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer_schema.dump(customer)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create customer', 'details': str(e)}), 500

@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(current_customer_id, customer_id):
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
        required: true
        schema:
          type: integer
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
        print(f"DEBUG: current_customer_id = {current_customer_id}, customer_id = {customer_id}")
        
        # Check authorization
        if int(current_customer_id) != customer_id:
            print("DEBUG: Authorization failed")
            return jsonify({'message': 'Unauthorized - can only delete your own account'}), 403
            
        customer = Customer.query.get_or_404(customer_id)
        print(f"DEBUG: Found customer: {customer.id}")
        
        # Delete associated vehicles first
        print(f"DEBUG: Deleting {len(customer.vehicles)} vehicles")
        for vehicle in customer.vehicles:
            # Delete any service tickets associated with this vehicle
            vehicle_tickets = ServiceTicket.query.filter_by(vehicle_id=vehicle.id).all()
            for ticket in vehicle_tickets:
                # Delete associated ticket parts
                ticket_parts = TicketPart.query.filter_by(ticket_id=ticket.id).all()
                for part in ticket_parts:
                    db.session.delete(part)
                db.session.delete(ticket)
            db.session.delete(vehicle)
        
        # Delete any remaining service tickets directly associated with customer
        customer_tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
        print(f"DEBUG: Deleting {len(customer_tickets)} remaining service tickets")
        for ticket in customer_tickets:
            # Delete associated ticket parts
            ticket_parts = TicketPart.query.filter_by(ticket_id=ticket.id).all()
            for part in ticket_parts:
                db.session.delete(part)
            db.session.delete(ticket)
        
        # Now delete the customer
        db.session.delete(customer)
        db.session.commit()
        
        print("DEBUG: Customer deleted successfully")
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error occurred: {str(e)}")
        return jsonify({'error': 'Failed to delete customer', 'details': str(e)}), 500
@customer_bp.route('/profile', methods=['GET'])
@token_required
def get_customer_profile(customer_id):
    """
    Get current customer profile
    ---
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
