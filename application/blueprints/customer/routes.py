from flask import request, jsonify
from application.extensions import db
from application.models import Customer
from application.blueprints.customer.customerSchemas import customer_schema, customers_schema, login_schema
from application.utils.jwt import encode_token, token_required
from . import customer_bp



@customer_bp.route('/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(customer_id):
    """Update a customer"""
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    errors = customer_schema.validate(data, partial=True)
    if errors:
        return jsonify({'errors': errors}), 400
    
    if 'name' in data:
        customer.name = data['name']
    if 'email' in data:
        existing = Customer.query.filter(
            Customer.email == data['email'],
            Customer.id != customer_id
        ).first()
        if existing:
            return jsonify({'error': 'Email already taken'}), 400
        customer.email = data['email']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'address' in data:
        customer.address = data['address']
    if 'password' in data:
        customer.set_password(data['password'])
    
    db.session.commit()
    return jsonify(customer_schema.dump(customer))

@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    """Delete a customer"""
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'})

@customer_bp.route('/register', methods=['POST'])
def register_customer():
    """Register a new customer"""
    data = request.get_json()
    
    errors = customer_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    existing_customer = Customer.query.filter_by(email=data.get('email')).first()
    if existing_customer:
        return jsonify({'error': 'Customer with this email already exists'}), 400
    
    new_customer = Customer(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    
    if 'password' in data:
        new_customer.set_password(data['password'])
    
    db.session.add(new_customer)
    db.session.commit()
    
    token = encode_token(new_customer.id, 'customer')
    
    return jsonify({
        'message': 'Customer created successfully',
        'token': token,
        'customer': customer_schema.dump(new_customer)
    }), 201

@customer_bp.route('/profile', methods=['GET'])
@token_required
def get_customer_profile():
    """Get current customer profile"""
    customer_id = getattr(request, 'user_id', None)
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer_schema.dump(customer))

@customer_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets():
    """Get service tickets for the current customer"""
    customer_id = getattr(request, 'user_id', None)
    
    from application.models import ServiceTicket
    from application.blueprints.service_ticket.serviceTicketSchemas import service_tickets_schema
    
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    
    return jsonify({
        'customer_id': customer_id,
        'tickets': service_tickets_schema.dump(tickets)
    })

customer_bp.route('/login', methods=['POST'])
def login_customer():
    """Customer login - SINGLE DEFINITION"""
    data = request.get_json()
    
    errors = login_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    customer = Customer.query.filter_by(email=data.get('email')).first()
    
    if customer and customer.check_password(data.get('password')):
        token = encode_token(customer.id, 'customer')
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'customer': customer_schema.dump(customer)
        })
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@customer_bp.route('/logout', methods=['POST'])
@token_required
def logout_customer():
    """Customer logout"""
    return jsonify({'message': 'Logout successful'})

@customer_bp.route('/', methods=['GET'])
@token_required
def get_all_customers():
    """Get all customers with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Customer.query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'customers': customers_schema.dump(pagination.items),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })

@customer_bp.route('/<int:customer_id>', methods=['GET'])
@token_required
def get_customer(customer_id):
    """Get a specific customer"""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer_schema.dump(customer))




