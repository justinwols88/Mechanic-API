# application/blueprints/vehicles/vehicle_schemas.py

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
import re

class VehicleSchema(Schema):
    """Schema for vehicle data"""
    
    id = fields.Int(dump_only=True)
    customer_id = fields.Int(required=True, error_messages={"required": "Customer ID is required"})
    make = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=50),
        error_messages={"required": "Make is required"}
    )
    model = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={"required": "Model is required"}
    )
    year = fields.Int(
        required=True,
        validate=validate.Range(min=1900, max=datetime.now().year + 1),
        error_messages={"required": "Year is required"}
    )
    vin = fields.Str(
        validate=validate.Length(equal=17, error="VIN must be exactly 17 characters"),
        allow_none=True
    )
    license_plate = fields.Str(
        validate=validate.Length(max=20),
        allow_none=True
    )
    color = fields.Str(
        validate=validate.Length(max=30),
        allow_none=True
    )
    mileage = fields.Int(
        validate=validate.Range(min=0),
        load_default=0
    )
    vehicle_type = fields.Str(
        validate=validate.Length(max=50),
        allow_none=True
    )
    fuel_type = fields.Str(
        validate=validate.OneOf([
            'gasoline', 'diesel', 'electric', 'hybrid', 'ethanol', 'cng', 'lpg', None
        ]),
        allow_none=True
    )
    transmission = fields.Str(
        validate=validate.OneOf(['automatic', 'manual', 'cvt', 'semi-automatic', None]),
        allow_none=True
    )
    engine_size = fields.Str(
        validate=validate.Length(max=20),
        allow_none=True
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('vin')
    def validate_vin_format(self, value):
        """Validate VIN format"""
        if value is None:
            return
        
        # Basic VIN validation - 17 alphanumeric characters, no I, O, Q
        if len(value) != 17:
            raise ValidationError("VIN must be exactly 17 characters")
        
        invalid_chars = set('IOQ')
        if any(char in invalid_chars for char in value.upper()):
            raise ValidationError("VIN cannot contain I, O, or Q")
        
        if not all(c.isalnum() for c in value):
            raise ValidationError("VIN must contain only alphanumeric characters")

class VehicleResponseSchema(Schema):
    """Schema for vehicle response with customer information"""
    
    id = fields.Int(dump_only=True)
    customer_id = fields.Int(required=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year = fields.Int(required=True)
    vin = fields.Str(required=True)
    license_plate = fields.Str(required=True)
    color = fields.Str(required=True)
    mileage = fields.Int(required=True)
    vehicle_type = fields.Str(required=True)
    fuel_type = fields.Str(required=True)
    transmission = fields.Str(required=True)
    engine_size = fields.Str(required=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    customer_name = fields.Str(required=True)
    customer_email = fields.Str(required=True)

# Initialize schemas
vehicle_schema = VehicleSchema()
vehicle_response_schema = VehicleResponseSchema()
vehicles_schema = VehicleSchema(many=True)

# application/blueprints/vehicles/vehicle_schemas.py
"""
Marshmallow schemas for vehicle data validation and serialization
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from datetime import datetime
import re

class VehicleCreateSchema(Schema):
    """Schema for creating a new vehicle"""
    
    customer_id = fields.Int(
        required=True,
        error_messages={"required": "Customer ID is required"}
    )
    make = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={"required": "Make is required"}
    )
    model = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={"required": "Model is required"}
    )
    year = fields.Int(
        required=True,
        validate=validate.Range(min=1900, max=datetime.now().year + 1),
        error_messages={"required": "Year is required"}
    )
    vin = fields.Str(
        validate=validate.Length(equal=17, error="VIN must be exactly 17 characters"),
        allow_none=True,
        load_default=None
    )
    license_plate = fields.Str(
        validate=validate.Length(max=20),
        allow_none=True,
        load_default=None
    )
    color = fields.Str(
        validate=validate.Length(max=30),
        allow_none=True,
        load_default=None
    )
    mileage = fields.Int(
        validate=validate.Range(min=0),
        load_default=0
    )
    vehicle_type = fields.Str(
        validate=validate.Length(max=50),
        allow_none=True,
        load_default=None
    )
    fuel_type = fields.Str(
        validate=validate.OneOf([
            'gasoline', 'diesel', 'electric', 'hybrid', 'ethanol', 'cng', 'lpg', ''
        ]),
        allow_none=True,
        load_default=None
    )
    transmission = fields.Str(
        validate=validate.OneOf(['automatic', 'manual', 'cvt', 'semi-automatic', '']),
        allow_none=True,
        load_default=None
    )
    engine_size = fields.Str(
        validate=validate.Length(max=20),
        allow_none=True,
        load_default=None
    )

    @validates('vin')
    def validate_vin_format(self, value):
        """Validate VIN format"""
        if not value:  # VIN is optional
            return
        
        if len(value) != 17:
            raise ValidationError("VIN must be exactly 17 characters")
        
        # VIN validation: 17 characters, no I, O, Q
        invalid_chars = set('IOQ')
        if any(char in invalid_chars for char in value.upper()):
            raise ValidationError("VIN cannot contain I, O, or Q")
        
        if not all(c.isalnum() for c in value):
            raise ValidationError("VIN must contain only alphanumeric characters")

    @validates('license_plate')
    def validate_license_plate(self, value):
        """Basic license plate validation"""
        if not value:
            return
        
        # Allow alphanumeric with spaces and hyphens
        if not re.match(r'^[A-Z0-9\s\-]+$', value.upper()):
            raise ValidationError("License plate can only contain letters, numbers, spaces, and hyphens")

class VehicleUpdateSchema(Schema):
    """Schema for updating vehicle data (all fields optional)"""
    
    make = fields.Str(validate=validate.Length(min=1, max=50))
    model = fields.Str(validate=validate.Length(min=1, max=50))
    year = fields.Int(validate=validate.Range(min=1900, max=datetime.now().year + 1))
    vin = fields.Str(
        validate=validate.Length(equal=17, error="VIN must be exactly 17 characters"),
        allow_none=True
    )
    license_plate = fields.Str(validate=validate.Length(max=20), allow_none=True)
    color = fields.Str(validate=validate.Length(max=30), allow_none=True)
    mileage = fields.Int(validate=validate.Range(min=0))
    vehicle_type = fields.Str(validate=validate.Length(max=50), allow_none=True)
    fuel_type = fields.Str(
        validate=validate.OneOf([
            'gasoline', 'diesel', 'electric', 'hybrid', 'ethanol', 'cng', 'lpg', ''
        ]),
        allow_none=True
    )
    transmission = fields.Str(
        validate=validate.OneOf(['automatic', 'manual', 'cvt', 'semi-automatic', '']),
        allow_none=True
    )
    engine_size = fields.Str(validate=validate.Length(max=20), allow_none=True)

class VehicleDetailResponseSchema(VehicleResponseSchema):
    """Schema for vehicle response with customer information"""
    
    customer_name = fields.Str()
    customer_email = fields.Str()
    service_tickets_count = fields.Int()

# Initialize schemas
vehicle_create_schema = VehicleCreateSchema()
vehicle_update_schema = VehicleUpdateSchema()
vehicle_response_schema = VehicleResponseSchema()
vehicle_detail_response_schema = VehicleDetailResponseSchema()
vehicles_response_schema = VehicleResponseSchema(many=True)