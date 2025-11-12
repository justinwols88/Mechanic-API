# application/blueprints/vehicles/routes.py
from application.models import Customer, ServiceTicket, db, Vehicle, Mechanic, Inventory, TicketPart
from application.extensions import db, cache
from.vehicle_schemas import vehicle_schema, vehicle_update_schema, vehicles_schema, vehicle_response_schema
from auth.tokens import mechanic_token_required, token_required, encode_token
from flask import Blueprint, request, jsonify
from .vehicle_schemas import vehicle_schema, vehicle_update_schema, vehicle_schema, vehicle_response_schema
from auth.tokens import token_required

# Create blueprint
vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

@vehicles_bp.route('/vehicles', methods=['POST'])
@token_required
def create_vehicle(current_user):
    """Create a new vehicle"""
    data = request.get_json()
    
    # Validate input data
    errors = vehicle_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Check if customer exists
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Check for duplicate VIN
    if data.get('vin'):
        existing_vehicle = Vehicle.get_by_vin(data['vin'])
        if existing_vehicle:
            return jsonify({'error': 'Vehicle with this VIN already exists'}), 409
    
    try:
        vehicle = Vehicle(**data)
        db.session.add(vehicle)
        db.session.commit()
        
        result = vehicle_response_schema.dump(vehicle.to_response_dict())
        return jsonify(result), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@vehicles_bp.route('/vehicles', methods=['GET'])
@token_required
def get_vehicles(current_user):
    """Get all vehicles (with optional customer_id filter)"""
    customer_id = request.args.get('customer_id')
    make = request.args.get('make')
    
    query = Vehicle.query
    
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if make:
        query = query.filter(Vehicle.make.ilike(f'%{make}%'))
    
    vehicles = query.all()
    result = vehicle_response_schema.dump([v.to_response_dict() for v in vehicles])
    return jsonify(result)

@vehicles_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
@token_required
def get_vehicle(current_user, vehicle_id):
    """Get a specific vehicle by ID"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    result = vehicle_response_schema.dump(vehicle.to_response_dict())
    return jsonify(result)

@vehicles_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
@token_required
def update_vehicle(current_user, vehicle_id):
    """Update a vehicle"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.get_json()
    
    # Validate input data
    errors = vehicle_update_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Check for duplicate VIN if provided
    if 'vin' in data and data['vin'] != vehicle.vin:
        existing_vehicle = Vehicle.get_by_vin(data['vin'])
        if existing_vehicle:
            return jsonify({'error': 'Vehicle with this VIN already exists'}), 409
    
    try:
        for key, value in data.items():
            if hasattr(vehicle, key):
                setattr(vehicle, key, value)
        
        db.session.commit()
        result = vehicle_response_schema.dump(vehicle.to_response_dict())
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@vehicles_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
@token_required
def delete_vehicle(current_user, vehicle_id):
    """Delete a vehicle"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    try:
        db.session.delete(vehicle)
        db.session.commit()
        return jsonify({'message': 'Vehicle deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@vehicles_bp.route('/customers/<int:customer_id>/vehicles', methods=['GET'])
@token_required
def get_customer_vehicles(current_user, customer_id):
    """Get all vehicles for a specific customer"""
    customer = Customer.query.get_or_404(customer_id)
    vehicles = Vehicle.query.filter_by(customer_id=customer_id).all()
    result = vehicle_response_schema.dump([v.to_response_dict() for v in vehicles])
    return jsonify(result)