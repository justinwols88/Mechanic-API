from flask import Blueprint, request, jsonify
from application.extensions import db
from application.models import ServiceTicket, Mechanic, Inventory, service_inventory
from auth.tokens import mechanic_token_required, token_required

service_ticket_bp = Blueprint('service_ticket', __name__)

# Add mechanics to ticket
@service_ticket_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@mechanic_token_required
def update_ticket_mechanics(mechanic_id, ticket_id):
    data = request.json
    remove_ids = data.get('remove_ids', [])
    add_ids = data.get('add_ids', [])
    
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    
    # Remove mechanics
    for mech_id in remove_ids:
        mechanic = Mechanic.query.get(mech_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
    
    # Add mechanics
    for mech_id in add_ids:
        mechanic = Mechanic.query.get(mech_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
    
    db.session.commit()
    return jsonify(ticket.to_dict())

# Add part to service ticket
@service_ticket_bp.route('/<int:ticket_id>/parts', methods=['POST'])
@mechanic_token_required
def add_part_to_ticket(mechanic_id, ticket_id):
    data = request.json
    part_id = data.get('part_id')
    quantity = data.get('quantity', 1)
    
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    part = Inventory.query.get_or_404(part_id)
    
    # Check if part already exists in ticket
    existing_assoc = db.session.execute(
        "SELECT * FROM service_inventory WHERE service_ticket_id = :ticket_id AND inventory_id = :part_id",
        {'ticket_id': ticket_id, 'part_id': part_id}
    ).first()
    
    if existing_assoc:
        # Update quantity
        db.session.execute(
            "UPDATE service_inventory SET quantity = quantity + :quantity WHERE service_ticket_id = :ticket_id AND inventory_id = :part_id",
            {'quantity': quantity, 'ticket_id': ticket_id, 'part_id': part_id}
        )
    else:
        # Add new association
        db.session.execute(
            "INSERT INTO service_inventory (service_ticket_id, inventory_id, quantity) VALUES (:ticket_id, :part_id, :quantity)",
            {'ticket_id': ticket_id, 'part_id': part_id, 'quantity': quantity}
        )
    
    db.session.commit()
    return jsonify(ticket.to_dict())

# Basic CRUD routes
@service_ticket_bp.route('/', methods=['GET'])
def get_service_tickets():
    tickets = ServiceTicket.query.all()
    return jsonify([ticket.to_dict() for ticket in tickets])

@service_ticket_bp.route('/', methods=['POST'])
@token_required
def create_service_ticket(customer_id):
    data = request.json
    data['customer_id'] = customer_id
    
    ticket = ServiceTicket(
        description=data['description'],
        customer_id=customer_id,
        priority=data.get('priority', 'normal')
    )
    
    db.session.add(ticket)
    db.session.commit()
    return jsonify(ticket.to_dict()), 201

@service_ticket_bp.route('/<int:ticket_id>', methods=['GET'])
def get_service_ticket(ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    return jsonify(ticket.to_dict())

@service_ticket_bp.route('/<int:ticket_id>', methods=['PUT'])
@mechanic_token_required
def update_service_ticket(mechanic_id, ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    data = request.json
    
    if 'description' in data:
        ticket.description = data['description']
    if 'status' in data:
        ticket.status = data['status']
    if 'priority' in data:
        ticket.priority = data['priority']
    
    db.session.commit()
    return jsonify(ticket.to_dict())

@service_ticket_bp.route('/<int:ticket_id>', methods=['DELETE'])
@mechanic_token_required
def delete_service_ticket(mechanic_id, ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return '', 204