from flask import Blueprint, request, jsonify
from application.utils.jwt import token_required
from application.extensions import limiter, cache, db
from application.models import ServiceTicket, ServiceTicketInventory, Mechanic, MechanicServiceTicketAssociation
from application.blueprints.service_ticket.serviceTicketSchemas import (
    service_ticket_schema, service_tickets_schema, 
    service_ticket_inventory_schema, service_ticket_inventories_schema
)

service_ticket_bp = Blueprint('service_ticket', __name__)

# Example cached route
@cache.cached(timeout=60, key_prefix='service_tickets_list')
@service_ticket_bp.route('/cached', methods=['GET'])
def cached_route():
    """Get service tickets with caching"""
    tickets = ServiceTicket.query.all()
    return jsonify(service_tickets_schema.dump(tickets))

# Example rate-limited route
@limiter.limit("10 per minute")
@service_ticket_bp.route('/rate-limited', methods=['GET'])
def rate_limited_route():
    return jsonify({"message": "This route is rate limited"})

# Get all service tickets
@service_ticket_bp.route('/', methods=['GET'])
@token_required
def get_all_service_tickets():
    """Get all service tickets"""
    tickets = ServiceTicket.query.all()
    return jsonify(service_tickets_schema.dump(tickets))

# Get specific service ticket
@service_ticket_bp.route('/<int:ticket_id>', methods=['GET'])
@token_required
def get_service_ticket(ticket_id):
    """Get a specific service ticket"""
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    return jsonify(service_ticket_schema.dump(ticket))

# Create new service ticket
@service_ticket_bp.route('/', methods=['POST'])
@token_required
def create_service_ticket():
    """Create a new service ticket"""
    data = request.get_json()
    
    errors = service_ticket_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    new_ticket = ServiceTicket(
        description=data.get('description'),
        customer_id=data.get('customer_id'),
        status=data.get('status', 'open'),
        priority=data.get('priority', 'normal'),
        vehicle_info=data.get('vehicle_info')
    )
    
    try:
        db.session.add(new_ticket)
        db.session.commit()
        cache.delete('service_tickets_list')  # Clear cache
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create service ticket', 'details': str(e)}), 500
    
    return jsonify(service_ticket_schema.dump(new_ticket)), 201

# Get all inventory associations for a service ticket
@service_ticket_bp.route('/<int:ticket_id>/inventory', methods=['GET'])
@token_required
def get_service_ticket_inventory(ticket_id):
    """Get all inventory items for a service ticket"""
    associations = ServiceTicketInventory.query.filter_by(service_ticket_id=ticket_id).all()
    if not associations:
        return jsonify({'message': 'No inventory items found for this ticket'}), 404

    return jsonify(service_ticket_inventories_schema.dump(associations))

# Add inventory to service ticket
@service_ticket_bp.route('/<int:ticket_id>/inventory', methods=['POST'])
@token_required
def add_inventory_to_ticket(ticket_id):
    """Add inventory item to service ticket"""
    data = request.get_json()
    
    # Check if service ticket exists
    service_ticket = ServiceTicket.query.get_or_404(ticket_id)
    
    # Check if inventory item exists
    from application.models import Inventory
    inventory_item = Inventory.query.get(data.get('inventory_id'))
    if not inventory_item:
        return jsonify({'error': 'Inventory item not found'}), 404
    
    # Check if association already exists
    existing = ServiceTicketInventory.query.filter_by(
        service_ticket_id=ticket_id,
        inventory_id=data.get('inventory_id')
    ).first()
    
    if existing:
        return jsonify({'error': 'This inventory item is already associated with the ticket'}), 400
    
    new_association = ServiceTicketInventory(
        service_ticket_id=ticket_id,
        inventory_id=data.get('inventory_id'),
        quantity_used=data.get('quantity_used', 1)
    )
    
    try:
        db.session.add(new_association)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add inventory to ticket', 'details': str(e)}), 500
    
    return jsonify(service_ticket_inventory_schema.dump(new_association)), 201

# Edit mechanics assigned to service ticket
@service_ticket_bp.route('/<int:ticket_id>/mechanics', methods=['PUT'])
@token_required
def edit_ticket_mechanics(ticket_id):
    """Add or remove mechanics from service ticket"""
    data = request.get_json()
    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])
    
    # Get current user ID from token
    current_user_id = getattr(request, 'user_id', None)
    
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    
    try:
        # Add mechanics
        for mechanic_id in add_ids:
            mechanic = Mechanic.query.get(mechanic_id)
            if mechanic:
                # Check if association already exists
                existing = MechanicServiceTicketAssociation.query.filter_by(
                    mechanic_id=mechanic_id,
                    service_ticket_id=ticket_id
                ).first()
                
                if not existing:
                    association = MechanicServiceTicketAssociation(
                        mechanic_id=mechanic_id,
                        service_ticket_id=ticket_id
                    )
                    db.session.add(association)
        
        # Remove mechanics
        for mechanic_id in remove_ids:
            association = MechanicServiceTicketAssociation.query.filter_by(
                mechanic_id=mechanic_id,
                service_ticket_id=ticket_id
            ).first()
            
            if association:
                db.session.delete(association)
        
        db.session.commit()
        cache.delete('service_tickets_list')  # Clear cache
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update ticket mechanics', 'details': str(e)}), 500
    
    return jsonify(service_ticket_schema.dump(ticket))

# Update service ticket
@service_ticket_bp.route('/<int:ticket_id>', methods=['PUT'])
@token_required
def update_service_ticket(ticket_id):
    """Update service ticket details"""
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    data = request.get_json()
    
    errors = service_ticket_schema.validate(data, partial=True)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Update fields
    updatable_fields = ['description', 'status', 'priority', 'vehicle_info', 
                       'payment_status', 'payment_amount', 'payment_method', 'payment_note']
    
    for field in updatable_fields:
        if field in data:
            setattr(ticket, field, data[field])
    
    # Handle payment date separately
    if 'payment_date' in data:
        ticket.payment_date = data['payment_date']  # This should be a date string
    
    try:
        db.session.commit()
        cache.delete('service_tickets_list')  # Clear cache
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update service ticket', 'details': str(e)}), 500
    
    return jsonify(service_ticket_schema.dump(ticket))

# Delete service ticket
@service_ticket_bp.route('/<int:ticket_id>', methods=['DELETE'])
@token_required
def delete_service_ticket(ticket_id):
    """Delete a service ticket"""
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    
    try:
        db.session.delete(ticket)
        db.session.commit()
        cache.delete('service_tickets_list')  # Clear cache
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete service ticket', 'details': str(e)}), 500
    
    return jsonify({'message': 'Service ticket deleted successfully'}), 200

# Get mechanics for a service ticket
@service_ticket_bp.route('/<int:ticket_id>/mechanics', methods=['GET'])
@token_required
def get_ticket_mechanics(ticket_id):
    """Get all mechanics assigned to a service ticket"""
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    
    # Assuming you have a relationship from ServiceTicket to Mechanic through the association table
    mechanics = [association.mechanic for association in ticket.mechanic_associations]
    
    from application.blueprints.mechanic.mechanicSchemas import mechanics_schema
    return jsonify(mechanics_schema.dump(mechanics))

@service_ticket_bp.route('/<int:ticket_id>/add-part', methods=['POST'])
@token_required
def add_part_to_ticket(ticket_id):
    """Add a single part to a service ticket"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('inventory_id') or not data.get('quantity'):
        return jsonify({'error': 'inventory_id and quantity are required'}), 400
    
    # Check if service ticket exists
    service_ticket = ServiceTicket.query.get_or_404(ticket_id)
    
    # Check if inventory item exists
    from application.models import Inventory
    inventory_item = Inventory.query.get(data.get('inventory_id'))
    if not inventory_item:
        return jsonify({'error': 'Inventory item not found'}), 404
    
    # Check if association already exists
    existing = ServiceTicketInventory.query.filter_by(
        service_ticket_id=ticket_id,
        inventory_id=data.get('inventory_id')
    ).first()
    
    if existing:
        # Update quantity if already exists
        existing.quantity_used = data.get('quantity')
    else:
        # Create new association
        new_association = ServiceTicketInventory(
            service_ticket_id=ticket_id,
            inventory_id=data.get('inventory_id'),
            quantity_used=data.get('quantity')
        )
        db.session.add(new_association)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Part added to ticket successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add part to ticket', 'details': str(e)}), 500