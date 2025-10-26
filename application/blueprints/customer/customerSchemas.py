from ...extensions import ma
from ...models import Customer

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True

class LoginSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Customer
    email = ma.Email(required=True)
    password = ma.String(required=True)

customer_schema = CustomerSchema()
login_schema = LoginSchema()
