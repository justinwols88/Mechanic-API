# application/schemas/mechanic_schema.py
from marshmallow import Schema, fields
class MechanicSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    specialization = fields.Str(required=True)
    phone = fields.Str()
    address = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

# Create instances
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
login_schema = LoginSchema()