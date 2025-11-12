from marshmallow import fields, validates, ValidationError, Schema
from datetime import datetime
from marshmallow.validate import Length, Range


class InventorySchema(Schema):
    id = fields.Int(dump_only=True)
    item_name = fields.Str(required=True)
    quantity = fields.Int(load_default=0)
    price = fields.Float()  # ✅ Use 'missing'
    description = fields.Str()  # ✅ Use 'missing'
    
    @validates('quantity')
    def validate_quantity(self, value):
        if value < 0:
            raise ValidationError('Quantity cannot be negative')

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)