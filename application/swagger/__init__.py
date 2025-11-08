from flasgger import Swagger
from flask import Blueprint

def init_swagger(app):
    """
    Initialize Swagger documentation
    """
    swagger_bp = Blueprint('swagger', __name__)
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "title": "Mechanic API Documentation",
        "uiversion": 3,
        "version": "1.0.0",
        "description": "A comprehensive API for managing auto repair shop operations"
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
    return swagger_bp

# Swagger template with definitions
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Mechanic API",
        "description": "API for managing mechanics, customers, inventory, and service tickets",
        "contact": {
            "email": "support@mechanicapi.com"
        },
        "version": "1.0.0"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "tags": [
        {
            "name": "Authentication",
            "description": "User authentication and token management"
        },
        {
            "name": "Mechanics",
            "description": "Mechanic management endpoints"
        },
        {
            "name": "Customers",
            "description": "Customer management endpoints"
        },
        {
            "name": "Inventory",
            "description": "Inventory management endpoints"
        },
        {
            "name": "Service Tickets",
            "description": "Service ticket management endpoints"
        }
    ]
}