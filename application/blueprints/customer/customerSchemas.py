# application/blueprints/customer/customerSchemas.py
from marshmallow import fields, Schema

class CustomerSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    password = fields.Str(load_only=True, required=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

# Initialize schemas
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()