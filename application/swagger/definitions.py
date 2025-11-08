"""
Swagger definitions for API data models
"""

# Authentication Definitions
login_definition = {
    "type": "object",
    "required": ["username", "password"],
    "properties": {
        "username": {
            "type": "string",
            "example": "test"
        },
        "password": {
            "type": "string",
            "example": "test"
        }
    }
}

login_response_definition = {
    "type": "object",
    "properties": {
        "access_token": {
            "type": "string",
            "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        },
        "token_type": {
            "type": "string",
            "example": "bearer"
        },
        "expires_in": {
            "type": "integer",
            "example": 86400
        }
    }
}

# Mechanic Definitions
mechanic_registration_definition = {
    "type": "object",
    "required": ["name", "email", "password", "specialization"],
    "properties": {
        "name": {
            "type": "string",
            "example": "John Doe"
        },
        "email": {
            "type": "string",
            "format": "email",
            "example": "john@example.com"
        },
        "password": {
            "type": "string",
            "example": "securepassword123"
        },
        "specialization": {
            "type": "string",
            "example": "Engine Repair"
        },
        "phone": {
            "type": "string",
            "example": "123-456-7890"
        },
        "address": {
            "type": "string",
            "example": "123 Main St, City, State"
        }
    }
}

mechanic_update_definition = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "example": "John Smith"
        },
        "email": {
            "type": "string",
            "format": "email",
            "example": "john.smith@example.com"
        },
        "specialization": {
            "type": "string",
            "example": "Transmission Repair"
        },
        "phone": {
            "type": "string",
            "example": "987-654-3210"
        },
        "address": {
            "type": "string",
            "example": "456 Oak Ave, City, State"
        },
        "password": {
            "type": "string",
            "example": "newpassword123"
        }
    }
}

mechanic_response_definition = {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
            "example": 1
        },
        "name": {
            "type": "string",
            "example": "John Doe"
        },
        "email": {
            "type": "string",
            "example": "john@example.com"
        },
        "specialization": {
            "type": "string",
            "example": "Engine Repair"
        },
        "phone": {
            "type": "string",
            "example": "123-456-7890"
        },
        "address": {
            "type": "string",
            "example": "123 Main St, City, State"
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "example": "2024-01-15T10:30:00Z"
        }
    }
}

# Customer Definitions
customer_registration_definition = {
    "type": "object",
    "required": ["name", "email"],
    "properties": {
        "name": {
            "type": "string",
            "example": "Jane Smith"
        },
        "email": {
            "type": "string",
            "format": "email",
            "example": "jane@example.com"
        },
        "phone": {
            "type": "string",
            "example": "555-123-4567"
        },
        "address": {
            "type": "string",
            "example": "789 Pine St, City, State"
        },
        "vehicle_info": {
            "type": "string",
            "example": "2020 Toyota Camry"
        }
    }
}

# Error Definitions
error_definition = {
    "type": "object",
    "properties": {
        "error": {
            "type": "string",
            "example": "Registration failed"
        },
        "message": {
            "type": "string",
            "example": "Internal server error occurred"
        },
        "details": {
            "type": "string",
            "example": "Database connection error"
        }
    }
}

validation_error_definition = {
    "type": "object",
    "properties": {
        "errors": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "example": {
                "email": ["Not a valid email address"],
                "password": ["Password must be at least 8 characters"]
            }
        }
    }
}

# Success Message Definition
success_message_definition = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string",
            "example": "Operation completed successfully"
        }
    }
}

# Service Ticket Definitions
service_ticket_definition = {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
            "example": 1
        },
        "customer_id": {
            "type": "integer",
            "example": 1
        },
        "description": {
            "type": "string",
            "example": "Engine overheating and strange noises"
        },
        "status": {
            "type": "string",
            "enum": ["pending", "in_progress", "completed", "cancelled"],
            "example": "pending"
        },
        "priority": {
            "type": "string",
            "enum": ["low", "normal", "high", "urgent"],
            "example": "normal"
        },
        "vehicle_info": {
            "type": "string",
            "example": "2020 Toyota Camry, VIN: 123456789"
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "example": "2024-01-15T10:30:00Z"
        },
        "updated_at": {
            "type": "string",
            "format": "date-time",
            "example": "2024-01-15T14:45:00Z"
        },
        "mechanics": {
            "type": "array",
            "items": {
                "$ref": "#/definitions/MechanicResponse"
            }
        },
        "parts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "part_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "name": {
                        "type": "string",
                        "example": "Engine Oil"
                    },
                    "quantity": {
                        "type": "integer",
                        "example": 2
                    }
                }
            }
        }
    }
}

service_ticket_create_definition = {
    "type": "object",
    "required": ["description"],
    "properties": {
        "description": {
            "type": "string",
            "example": "Engine overheating and strange noises"
        },
        "priority": {
            "type": "string",
            "enum": ["low", "normal", "high", "urgent"],
            "example": "normal"
        },
        "vehicle_info": {
            "type": "string",
            "example": "2020 Toyota Camry, VIN: 123456789"
        }
    }
}

service_ticket_update_definition = {
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
            "example": "Updated description of the issue"
        },
        "status": {
            "type": "string",
            "enum": ["pending", "in_progress", "completed", "cancelled"],
            "example": "in_progress"
        },
        "priority": {
            "type": "string",
            "enum": ["low", "normal", "high", "urgent"],
            "example": "high"
        }
    }
}

inventory_item_definition = {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
            "example": 1
        },
        "name": {
            "type": "string",
            "example": "Engine Oil"
        },
        "description": {
            "type": "string",
            "example": "Synthetic engine oil 5W-30"
        },
        "price": {
            "type": "number",
            "format": "float",
            "example": 29.99
        },
        "quantity": {
            "type": "integer",
            "example": 50
        },
        "category": {
            "type": "string",
            "example": "Lubricants"
        },
        "min_stock_level": {
            "type": "integer",
            "example": 10
        },
        "supplier": {
            "type": "string",
            "example": "AutoParts Inc."
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "example": "2024-01-15T10:30:00Z"
        },
        "updated_at": {
            "type": "string",
            "format": "date-time",
            "example": "2024-01-15T14:45:00Z"
        }
    }
}

inventory_create_definition = {
    "type": "object",
    "required": ["item_name"],
    "properties": {
        "item_name": {
            "type": "string",
            "example": "Engine Oil"
        },
        "price": {
            "type": "number",
            "format": "float",
            "example": 29.99
        },
        "quantity": {
            "type": "integer",
            "example": 50
        },
        "description": {
            "type": "string",
            "example": "Synthetic engine oil 5W-30"
        },
        "category": {
            "type": "string",
            "example": "Lubricants"
        },
        "min_stock_level": {
            "type": "integer",
            "example": 10
        },
        "supplier": {
            "type": "string",
            "example": "AutoParts Inc."
        }
    }
}

inventory_update_definition = {
    "type": "object",
    "properties": {
        "item_name": {
            "type": "string",
            "example": "Premium Engine Oil"
        },
        "price": {
            "type": "number",
            "format": "float",
            "example": 34.99
        },
        "quantity": {
            "type": "integer",
            "example": 45
        },
        "description": {
            "type": "string",
            "example": "Premium synthetic engine oil 5W-30"
        },
        "category": {
            "type": "string",
            "example": "Lubricants"
        },
        "min_stock_level": {
            "type": "integer",
            "example": 15
        },
        "supplier": {
            "type": "string",
            "example": "Premium AutoParts Inc."
        }
    }
}

# Customer Definitions
customer_definition = {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
            "example": 1
        },
        "name": {
            "type": "string",
            "example": "John Doe"
        },
        "email": {
            "type": "string",
            "format": "email",
            "example": "john@example.com"
        },
        "phone": {
            "type": "string",
            "example": "123-456-7890"
        },
        "address": {
            "type": "string",
            "example": "123 Main St, City, State"
        },
        "vehicle_info": {
            "type": "string",
            "example": "2020 Toyota Camry, VIN: 123456789"
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "example": "2024-01-15T10:30:00Z"
        },
        "updated_at": {
            "type": "string",
            "format": "date-time",
            "example": "2024-01-15T14:45:00Z"
        }
    }
}

customer_registration_definition = {
    "type": "object",
    "required": ["name", "email", "password"],
    "properties": {
        "name": {
            "type": "string",
            "example": "John Doe"
        },
        "email": {
            "type": "string",
            "format": "email",
            "example": "john@example.com"
        },
        "password": {
            "type": "string",
            "example": "securepassword123"
        },
        "phone": {
            "type": "string",
            "example": "123-456-7890"
        },
        "address": {
            "type": "string",
            "example": "123 Main St, City, State"
        },
        "vehicle_info": {
            "type": "string",
            "example": "2020 Toyota Camry, VIN: 123456789"
        }
    }
}

customer_update_definition = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "example": "John Smith"
        },
        "email": {
            "type": "string",
            "format": "email",
            "example": "john.smith@example.com"
        },
        "phone": {
            "type": "string",
            "example": "987-654-3210"
        },
        "address": {
            "type": "string",
            "example": "456 Oak Ave, City, State"
        },
        "vehicle_info": {
            "type": "string",
            "example": "2021 Honda Civic, VIN: 987654321"
        },
        "password": {
            "type": "string",
            "example": "newpassword123"
        }
    }
}