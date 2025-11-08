from flask import Blueprint, request, jsonify
from application.extensions import db
from application.models import ServiceTicket, Mechanic, Inventory, service_inventory
from auth.tokens import mechanic_token_required, token_required
from . import service_ticket_bp  # This imports the blueprint instance
from flask import request, jsonify
# ... other imports

# Make sure all routes are using @service_ticket_bp.route, not @app.route

@service_ticket_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@mechanic_token_required
def update_ticket_mechanics(mechanic_id, ticket_id):
    """
    Update mechanics assigned to a service ticket
    ---
    tags:
      - Service Tickets
    security:
      - BearerAuth: []
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            remove_ids:
              type: array
              items:
                type: integer
              example: [2, 3]
              description: List of mechanic IDs to remove from ticket
            add_ids:
              type: array
              items:
                type: integer
              example: [4, 5]
              description: List of mechanic IDs to add to ticket
    responses:
      200:
        description: Ticket mechanics updated successfully
        schema:
          $ref: '#/definitions/ServiceTicket'
      400:
        description: Invalid request data
        schema:
          $ref: '#/definitions/Error'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Ticket not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update ticket mechanics', 'details': str(e)}), 500

@service_ticket_bp.route('/<int:ticket_id>/parts', methods=['POST'])
@mechanic_token_required
def add_part_to_ticket(mechanic_id, ticket_id):
    """
    Add parts/inventory to service ticket
    ---
    tags:
      - Service Tickets
    security:
      - BearerAuth: []
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - part_id
          properties:
            part_id:
              type: integer
              example: 1
              description: Inventory item ID to add to ticket
            quantity:
              type: integer
              example: 2
              description: Quantity of the part to use
              default: 1
    responses:
      200:
        description: Part added to ticket successfully
        schema:
          $ref: '#/definitions/ServiceTicket'
      400:
        description: Invalid request data
        schema:
          $ref: '#/definitions/Error'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Ticket or part not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        data = request.json
        part_id = data.get('part_id')
        quantity = data.get('quantity', 1)
        
        if not part_id:
            return jsonify({'error': 'Part ID is required'}), 400
        
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add part to ticket', 'details': str(e)}), 500

@service_ticket_bp.route('/', methods=['GET'])
def get_service_tickets():
    """
    Get all service tickets
    ---
    tags:
      - Service Tickets
    responses:
      200:
        description: Service tickets retrieved successfully
        schema:
          type: array
          items:
            $ref: '#/definitions/ServiceTicket'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        tickets = ServiceTicket.query.all()
        return jsonify([ticket.to_dict() for ticket in tickets])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve service tickets', 'details': str(e)}), 500

@service_ticket_bp.route('/', methods=['POST'])
@token_required
def create_service_ticket(customer_id):
    """
    Create a new service ticket
    ---
    tags:
      - Service Tickets
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - description
          properties:
            description:
              type: string
              example: "Engine overheating and strange noises"
            priority:
              type: string
              enum: [low, normal, high, urgent]
              example: "normal"
              default: "normal"
            vehicle_info:
              type: string
              example: "2020 Toyota Camry, VIN: 123456789"
    responses:
      201:
        description: Service ticket created successfully
        schema:
          $ref: '#/definitions/ServiceTicket'
      400:
        description: Missing required fields
        schema:
          $ref: '#/definitions/Error'
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
        data = request.json
        
        if not data.get('description'):
            return jsonify({'error': 'Description is required'}), 400
        
        ticket = ServiceTicket(
            description=data['description'],
            customer_id=customer_id,
            priority=data.get('priority', 'normal'),
            vehicle_info=data.get('vehicle_info', '')
        )
        
        db.session.add(ticket)
        db.session.commit()
        return jsonify(ticket.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create service ticket', 'details': str(e)}), 500

@service_ticket_bp.route('/<int:ticket_id>', methods=['GET'])
def get_service_ticket(ticket_id):
    """
    Get specific service ticket by ID
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Service ticket retrieved successfully
        schema:
          $ref: '#/definitions/ServiceTicket'
      404:
        description: Ticket not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        ticket = ServiceTicket.query.get_or_404(ticket_id)
        return jsonify(ticket.to_dict())
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve service ticket', 'details': str(e)}), 500

@service_ticket_bp.route('/<int:ticket_id>', methods=['PUT'])
@mechanic_token_required
def update_service_ticket(mechanic_id, ticket_id):
    """
    Update service ticket
    ---
    tags:
      - Service Tickets
    security:
      - BearerAuth: []
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            description:
              type: string
              example: "Updated description of the issue"
            status:
              type: string
              enum: [pending, in_progress, completed, cancelled]
              example: "in_progress"
            priority:
              type: string
              enum: [low, normal, high, urgent]
              example: "high"
    responses:
      200:
        description: Service ticket updated successfully
        schema:
          $ref: '#/definitions/ServiceTicket'
      400:
        description: Invalid request data
        schema:
          $ref: '#/definitions/Error'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Ticket not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update service ticket', 'details': str(e)}), 500

@service_ticket_bp.route('/<int:ticket_id>', methods=['DELETE'])
@mechanic_token_required
def delete_service_ticket(mechanic_id, ticket_id):
    """
    Delete service ticket
    ---
    tags:
      - Service Tickets
    security:
      - BearerAuth: []
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      204:
        description: Service ticket deleted successfully
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Ticket not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        ticket = ServiceTicket.query.get_or_404(ticket_id)
        db.session.delete(ticket)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete service ticket', 'details': str(e)}), 500