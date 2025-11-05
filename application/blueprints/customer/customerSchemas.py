from marshmallow import fields, validates, ValidationError, Schema
from application.extensions import ma

class CustomerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str(load_default="")
    address = fields.Str(load_default="")
    password = fields.Str(load_only=True, required=True)
    
    @validates('email')
    def validate_email(self, value):
        if len(value) < 3:
            raise ValidationError('Email must be at least 3 characters long')

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()