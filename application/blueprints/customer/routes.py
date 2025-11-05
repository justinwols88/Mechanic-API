# mechanic/routes.py
from flask import Blueprint, request, jsonify
from application.extensions import db
from application.models import Mechanic, service_mechanic
from application.blueprints.mechanic.mechanicSchemas import mechanic_schema, mechanics_schema, login_schema
from auth.tokens import encode_mechanic_token, mechanic_token_required
from sqlalchemy import func, desc

mechanic_bp = Blueprint('mechanic', __name__)

# Mechanic Login
from flask import Blueprint, request, jsonify
from application.extensions import db, limiter, cache
from application.models import Customer, ServiceTicket
from application.blueprints.customer.customerSchemas import customer_schema, customers_schema, login_schema
from auth.tokens import encode_token, token_required

customer_bp = Blueprint('customer', __name__)

# Apply default rate limiting to all customer routes
@customer_bp.before_request
@limiter.limit("100 per hour")
def before_request():
    pass

# Customer Login
@customer_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
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

# Get customer's tickets (token required)
@customer_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return jsonify([ticket.to_dict() for ticket in tickets])

# Get all customers with pagination and caching
@customer_bp.route('/', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_customers():
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

# Other CRUD routes
@customer_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer_schema.dump(customer))

@customer_bp.route('/', methods=['POST'])
def create_customer():
    data = request.json
    errors = customer_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    customer = customer_schema.load(data)
    customer.set_password(data['password'])
    
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer_schema.dump(customer)), 201

@customer_bp.route('/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(customer_id, token_customer_id):
    if customer_id != int(token_customer_id):
        return jsonify({'message': 'Unauthorized'}), 403
        
    customer = Customer.query.get_or_404(customer_id)
    data = request.json
    customer = customer_schema.load(data, instance=customer)
    db.session.commit()
    return jsonify(customer_schema.dump(customer))

@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(customer_id, token_customer_id):
    if customer_id != int(token_customer_id):
        return jsonify({'message': 'Unauthorized'}), 403
        
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return '', 204

# Mechanic Leaderboard
@mechanic_bp.route('/leaderboard', methods=['GET'])
def get_mechanics_leaderboard():
    mechanics = Mechanic.query\
        .outerjoin(service_mechanic)\
        .group_by(Mechanic.id)\
        .order_by(desc(func.count(service_mechanic.c.mechanic_id)))\
        .all()
    
    return jsonify([{
        'mechanic': mechanic_schema.dump(mechanic),
        'ticket_count': len(mechanic.service_tickets)
    } for mechanic in mechanics])

# Other CRUD routes for mechanics (with mechanic token required for some)
@mechanic_bp.route('/', methods=['GET'])
def get_mechanics():
    mechanics = Mechanic.query.all()
    return jsonify(mechanics_schema.dump(mechanics))

@mechanic_bp.route('/<int:mechanic_id>', methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    return jsonify(mechanic_schema.dump(mechanic))

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
    if mechanic_id != token_mechanic_id:
        return jsonify({'message': 'Unauthorized'}), 403
        
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    data = request.json
    mechanic = mechanic_schema.load(data, instance=mechanic)
    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic))

@mechanic_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@mechanic_token_required
def delete_mechanic(mechanic_id, token_mechanic_id):
    if mechanic_id != token_mechanic_id:
        return jsonify({'message': 'Unauthorized'}), 403
        
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    db.session.delete(mechanic)
    db.session.commit()
    return '', 204