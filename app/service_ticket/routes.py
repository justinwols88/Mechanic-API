from flask import request, jsonify
from app.service_ticket import service_ticket_bp
from app.models import ServiceTicket, Mechanic
from app import db
from app.service_ticket.schemas import service_ticket_schema, service_tickets_schema
from app.customer.routes import token_required

@service_ticket_bp.route('/', methods=['POST'])
@token_required
def create_service_ticket(customer_id):
    """
    Create service ticket - requires authentication
    The customer_id comes from the token_required decorator
    """
    try:
        data = request.get_json()
        
        # Add customer_id from token to the ticket data
        data['customer_id'] = customer_id
        
        errors = service_ticket_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400
        
        service_ticket = service_ticket_schema.load(data)
        db.session.add(service_ticket)
        db.session.commit()
        
        return service_ticket_schema.jsonify(service_ticket), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@service_ticket_bp.route('/', methods=['GET'])
@token_required
def get_service_tickets(customer_id):
    """
    Get all service tickets - requires authentication
    """
    try:
        service_tickets = ServiceTicket.query.all()
        return service_tickets_schema.jsonify(service_tickets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# These routes might also need protection in a real application
@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    try:
        service_ticket = ServiceTicket.query.get_or_404(ticket_id)
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        if mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)
            db.session.commit()
        
        return service_ticket_schema.jsonify(service_ticket)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    try:
        service_ticket = ServiceTicket.query.get_or_404(ticket_id)
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        if mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)
            db.session.commit()
        
        return service_ticket_schema.jsonify(service_ticket)
    except Exception as e:
        return jsonify({"error": str(e)}), 500