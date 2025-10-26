from flask import Blueprint, jsonify, request
from ...extensions import db, cache
from ...models import ServiceTicket, Mechanic
from .serviceTicketSchemas import service_ticket_schema, service_tickets_schema
from ...utils.jwt import token_required

service_ticket_bp = Blueprint('service_ticket_bp', __name__, url_prefix='/service-tickets')

@service_ticket_bp.route('/', methods=['POST'])
def create_ticket():
    data = request.get_json()
    ticket = ServiceTicket(**data)
    db.session.add(ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 201

@service_ticket_bp.route('/', methods=['GET'])
@cache.cached(timeout=120)
def get_all_tickets():
    tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(tickets), 200

@service_ticket_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return service_tickets_schema.jsonify(tickets), 200

@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200

@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200
