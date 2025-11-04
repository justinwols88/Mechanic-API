from marshmallow import fields, validates, ValidationError, Schema
from application.extensions import ma

class MechanicSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str()  # ✅ Use 'missing'
    specialization = fields.Str()  # ✅ Use 'missing'
    password = fields.Str(load_only=True, required=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
login_schema = LoginSchema()