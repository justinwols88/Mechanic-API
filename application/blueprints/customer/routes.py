from flask import Blueprint, request, jsonify
from ...extensions import db
from ...models import Customer
from ...utils.jwt import encode_token, token_required
from .customerSchemas import customer_schema, login_schema
from ...extensions import limiter

customer_bp = Blueprint('customer_bp', __name__, url_prefix='/customers')

@customer_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    new_customer = Customer(name=data['name'], email=data['email'])
    new_customer.set_password(data['password'])
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

@customer_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    errors = login_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    customer = Customer.query.filter_by(email=data['email']).first()
    if not customer or not customer.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    token = encode_token(customer.id)
    return jsonify({'token': token}), 200

# Example protected route
@customer_bp.route('/profile', methods=['GET'])
@token_required
def profile(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return customer_schema.jsonify(customer), 200
