from flask import Blueprint, request, jsonify
from application.models import Inventory
from application.blueprints.inventory.inventorySchemas import inventory_schema, inventories_schema
from application.extensions import db, limiter, cache
from application.utils.jwt import token_required

inventory_bp = Blueprint('inventory', __name__)

# Example cached route
@cache.cached(timeout=60, key_prefix='inventory_list')
@inventory_bp.route('/cached', methods=['GET'])
def get_cached_inventory():
    """Get inventory with caching"""
    items = Inventory.query.all()
    return jsonify(inventories_schema.dump(items))

# Example rate-limited route
@limiter.limit("10 per minute")
@inventory_bp.route('/rate-limited', methods=['GET'])
def rate_limited_example():
    return jsonify({"message": "This route is rate limited"})

# Main inventory routes
@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    """Get all inventory items"""
    items = Inventory.query.all()
    return jsonify(inventories_schema.dump(items))

@inventory_bp.route('/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    """Get a specific inventory item"""
    item = Inventory.query.get_or_404(item_id)
    return jsonify(inventory_schema.dump(item))

@inventory_bp.route('/', methods=['POST'])
@token_required
def add_inventory_item():
    """Add a new inventory item"""
    data = request.get_json()
    
    # Validation
    errors = inventory_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Check if item already exists
    existing_item = Inventory.query.filter_by(item_name=data.get('item_name')).first()
    if existing_item:
        return jsonify({'error': 'Item with this name already exists'}), 400

    new_item = Inventory(
        item_name=data.get('item_name'),
        quantity=data.get('quantity', 0),
        price=data.get('price', 0.0),  # Added price field
        description=data.get('description', '')  # Added description field
    )
    
    try:
        db.session.add(new_item)
        db.session.commit()
        # Clear cache when new item is added
        cache.delete('inventory_list')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add item', 'details': str(e)}), 500

    return jsonify(inventory_schema.dump(new_item)), 201

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@token_required
def update_inventory_item(item_id):
    """Update an inventory item"""
    item = Inventory.query.get_or_404(item_id)
    data = request.get_json()
    
    # Partial validation for updates
    errors = inventory_schema.validate(data, partial=True)
    if errors:
        return jsonify({'errors': errors}), 400

    # Update fields if provided
    if 'item_name' in data:
        # Check if new name conflicts with other items
        existing = Inventory.query.filter(
            Inventory.item_name == data['item_name'],
            Inventory.id != item_id
        ).first()
        if existing:
            return jsonify({'error': 'Another item with this name already exists'}), 400
        item.item_name = data['item_name']
    
    if 'quantity' in data:
        item.quantity = data['quantity']
    
    if 'price' in data:
        item.price = data['price']
    
    if 'description' in data:
        item.description = data['description']

    try:
        db.session.commit()
        # Clear cache when item is updated
        cache.delete('inventory_list')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update item', 'details': str(e)}), 500

    return jsonify(inventory_schema.dump(item))

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
@token_required
def delete_inventory_item(item_id):
    """Delete an inventory item"""
    item = Inventory.query.get_or_404(item_id)
    
    # Check if item is used in any service tickets
    from application.models import ServiceTicketInventory
    usage_count = ServiceTicketInventory.query.filter_by(inventory_id=item_id).count()
    if usage_count > 0:
        return jsonify({
            'error': 'Cannot delete item', 
            'message': f'This item is used in {usage_count} service ticket(s)'
        }), 400
    
    try:
        db.session.delete(item)
        db.session.commit()
        # Clear cache when item is deleted
        cache.delete('inventory_list')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete item', 'details': str(e)}), 500

    return jsonify({"message": "Item deleted successfully"}), 200

# Search and filter routes
@inventory_bp.route('/search', methods=['GET'])
def search_inventory():
    """Search inventory by name"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    items = Inventory.query.filter(Inventory.item_name.ilike(f'%{query}%')).all()
    return jsonify(inventories_schema.dump(items))

@inventory_bp.route('/low-stock', methods=['GET'])
def get_low_stock():
    """Get items with low quantity (less than 10)"""
    low_stock_items = Inventory.query.filter(Inventory.quantity < 10).all()
    return jsonify(inventories_schema.dump(low_stock_items))

# Bulk operations
@inventory_bp.route('/bulk-update', methods=['PUT'])
@token_required
def bulk_update_inventory():
    """Update multiple inventory items at once"""
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of items'}), 400
    
    updated_items = []
    
    try:
        for item_data in data:
            item_id = item_data.get('id')
            if not item_id:
                continue
                
            item = Inventory.query.get(item_id)
            if item:
                if 'quantity' in item_data:
                    item.quantity = item_data['quantity']
                if 'price' in item_data:
                    item.price = item_data['price']
                updated_items.append(item)
        
        db.session.commit()
        cache.delete('inventory_list')
        
        return jsonify({
            'message': f'Successfully updated {len(updated_items)} items',
            'items': inventories_schema.dump(updated_items)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update items', 'details': str(e)}),500
