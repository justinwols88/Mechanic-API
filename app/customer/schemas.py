from app import ma
from app.models import Customer
from marshmallow import fields

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        exclude = ('password_hash',)  # Never include password hash in responses

# Login schema with only email and password fields
class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()