# Import necessary modules and blueprints
from application.models import Customer, ServiceTicket, db
from application.extensions import db, cache
from flask import blueprints, request, jsonify
from flask_jwt_extended import jwt_required
from auth.tokens import mechanic_token_required, token_required, encode_token
from . import service_ticket_bp  # Import from __init__.py

@service_ticket_bp.route('/api/service-tickets', methods=['GET'])
@jwt_required()
def get_service_tickets():
    """Get all service tickets"""
    return jsonify({"message": "Service tickets endpoint", "data": []})

@service_ticket_bp.route('/api/service-tickets', methods=['POST'])
@jwt_required()
def create_service_ticket():
    """Create a new service ticket"""
    data = request.get_json()
    return jsonify({"message": "Service ticket created", "data": data}), 201

@service_ticket_bp.route('/api/service-tickets/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_service_ticket(ticket_id):
    """Get a specific service ticket"""
    return jsonify({"message": f"Service ticket {ticket_id}", "data": {}})

@service_ticket_bp.route('/api/service-tickets/<int:ticket_id>', methods=['PUT'])
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
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
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

@service_ticket_bp.route('/api/service-tickets/<int:ticket_id>', methods=['DELETE'])
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