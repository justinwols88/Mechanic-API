from .definitions import *

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Mechanic API",
        "description": "API for managing auto repair shop operations",
        "version": "1.0.0",
        "contact": {
            "email": "support@mechanicapi.com"
        }
    },
    "host": "localhost:5000", 
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization", 
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme"
        }
    },
    "tags": [
        {"name": "Authentication", "description": "User authentication"},
        {"name": "Mechanics", "description": "Mechanic management"},
        {"name": "Customers", "description": "Customer management"},
        {"name": "Inventory", "description": "Inventory management"},
        {"name": "Service Tickets", "description": "Service ticket management"}
    ],
    "definitions": {
        "Login": login_definition,
        "LoginResponse": login_response_definition,
        "MechanicRegistration": mechanic_registration_definition,
        "MechanicUpdate": mechanic_update_definition,
        "MechanicResponse": mechanic_response_definition,
        "CustomerRegistration": customer_registration_definition,
        "Error": error_definition,
        "ValidationError": validation_error_definition,
        "SuccessMessage": success_message_definition,
        "ServiceTicket": service_ticket_definition,
        "ServiceTicketCreate": service_ticket_create_definition,
        "ServiceTicketUpdate": service_ticket_update_definition,
        "InventoryItem": inventory_item_definition,
        "InventoryCreate": inventory_create_definition,
        "InventoryUpdate": inventory_update_definition,
        "Customer": customer_definition,
        "CustomerRegistration": customer_registration_definition,
        "CustomerUpdate": customer_update_definition,
    }
}