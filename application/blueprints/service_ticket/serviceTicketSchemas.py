from marshmallow import fields, validates, ValidationError
from application.extensions import ma
from application.models import ServiceTicket, Mechanic, Inventory, TicketPart

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True
        fields = ("id", "description", "date_created", "customer_id", "status", "priority", "payment_status")

    # Explicit field declarations
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    date_created = fields.DateTime(dump_only=True)
    customer_id = fields.Int(required=True)
    status = fields.Str(load_default="pending")
    priority = fields.Str(load_default="normal")
    payment_status = fields.Str(load_default="N/A")

class ServiceTicketCreateSchema(ma.Schema):
    """Manual schema for creating service tickets"""
    description = fields.Str(required=True)
    customer_id = fields.Int(required=True)
    priority = fields.Str(load_default="normal")

# Initialize schemas
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
service_ticket_create_schema = ServiceTicketCreateSchema()