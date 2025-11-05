from flask import request, jsonify
from application.blueprints.inventory import inventory_bp
from application.models import Inventory, db
from application.blueprints.inventory.inventorySchemas import inventory_schema, inventories_schema
from auth.tokens import mechanic_token_required

# CRUD routes for inventory
@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    items = Inventory.query.all()
    return jsonify([item.to_dict() for item in items])

@inventory_bp.route('/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    item = Inventory.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@inventory_bp.route('/', methods=['POST'])
@mechanic_token_required
def create_inventory_item(mechanic_id):
    data = request.json
    errors = inventory_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    item = Inventory(
        name=data['item_name'],
        price=data.get('price', 0.0),
        quantity=data.get('quantity', 0),
        description=data.get('description', '')
    )
    
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@mechanic_token_required
def update_inventory_item(mechanic_id, item_id):
    item = Inventory.query.get_or_404(item_id)
    data = request.json
    
    if 'item_name' in data:
        item.name = data['item_name']
    if 'price' in data:
        item.price = data['price']
    if 'quantity' in data:
        item.quantity = data['quantity']
    if 'description' in data:
        item.description = data['description']
    
    db.session.commit()
    return jsonify(item.to_dict())

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
@mechanic_token_required
def delete_inventory_item(mechanic_id, item_id):
    item = Inventory.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return '', 204