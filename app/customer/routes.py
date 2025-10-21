from flask import request, jsonify
from app.customer import customer_bp
from app.models import Customer, ServiceTicket, encode_token, decode_token
from app import db
from app.customer.schemas import customer_schema, login_schema
from app.service_ticket.schemas import service_tickets_schema
from functools import wraps

def token_required(f):
    """
    Token validation decorator
    Validates the Bearer token and passes customer_id to the decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Extract token from "Bearer <token>"
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                else:
                    return jsonify({'message': 'Invalid token format. Use: Bearer <token>'}), 401
            except IndexError:
                return jsonify({'message': 'Invalid token format. Use: Bearer <token>'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Decode the token to get customer_id
            customer_id = decode_token(token)
            
            # Check if decode returned an error message
            if isinstance(customer_id, str):
                return jsonify({'message': customer_id}), 401
            
            # Verify customer exists
            customer = Customer.query.get(customer_id)
            if not customer:
                return jsonify({'message': 'Customer not found!'}), 401
            
            # Add customer_id to kwargs for the decorated function
            kwargs['customer_id'] = customer_id
            
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@customer_bp.route('/login', methods=['POST'])
def login():
    """
    Customer login - validates credentials and returns JWT token
    """
    try:
        data = request.get_json()
        
        # Validate login data
        errors = login_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400
        
        # Find customer by email
        customer = Customer.query.filter_by(email=data['email']).first()
        
        if not customer or not customer.check_password(data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Generate token using the encode_token function
        token = encode_token(customer.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'customer_id': customer.id
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@customer_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    """
    Get service tickets for the authenticated customer
    Requires Bearer Token authorization
    """
    try:
        # Query service tickets for this customer using the customer_id from token
        service_tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
        
        return service_tickets_schema.jsonify(service_tickets)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Additional customer routes that should require authorization
@customer_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(customer_id):
    """
    Get customer profile - requires authentication
    """
    try:
        customer = Customer.query.get_or_404(customer_id)
        return customer_schema.jsonify(customer)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@customer_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(customer_id):
    """
    Update customer profile - requires authentication
    """
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        errors = customer_schema.validate(data, partial=True)
        if errors:
            return jsonify({"errors": errors}), 400
        
        customer = customer_schema.load(data, instance=customer, partial=True)
        db.session.commit()
        
        return customer_schema.jsonify(customer)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@customer_bp.route('/register', methods=['POST'])
def register_customer():
    """
    Register a new customer (for testing purposes)
    """
    try:
        data = request.get_json()
        
        # Check if customer already exists
        existing_customer = Customer.query.filter_by(email=data.get('email')).first()
        if existing_customer:
            return jsonify({'message': 'Customer with this email already exists'}), 400
        
        # Create customer
        customer = Customer(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone')
        )
        customer.set_password(data['password'])
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'message': 'Customer registered successfully',
            'customer_id': customer.id
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500