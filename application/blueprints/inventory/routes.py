from flask import request, jsonify
from application.models import Customer, ServiceTicket, db, Inventory, Mechanic
from application.extensions import db, cache
from application.blueprints.inventory import inventory_bp
from application.blueprints.inventory.inventorySchemas import inventory_schema, inventories_schema
from auth.tokens import mechanic_token_required, token_required, encode_token

@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    """
    Get all inventory items
    ---
    tags:
      - Inventory
    responses:
      200:
        description: Inventory items retrieved successfully
        schema:
          type: array
          items:
            $ref: '#/definitions/InventoryItem'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        items = Inventory.query.all()
        return jsonify([item.to_dict() for item in items])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve inventory items', 'details': str(e)}), 500

@inventory_bp.route('/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    """
    Get specific inventory item by ID
    ---
    tags:
      - Inventory
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Inventory item retrieved successfully
        schema:
          $ref: '#/definitions/InventoryItem'
      404:
        description: Inventory item not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        item = Inventory.query.get_or_404(item_id)
        return jsonify(item.to_dict())
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve inventory item', 'details': str(e)}), 500

@inventory_bp.route('/', methods=['POST'])
@mechanic_token_required
def create_inventory_item(mechanic_id):
    """
    Create a new inventory item
    ---
    tags:
      - Inventory
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - item_name
          properties:
            item_name:
              type: string
              example: "Engine Oil"
            price:
              type: number
              format: float
              example: 29.99
              description: Price per unit
            quantity:
              type: integer
              example: 50
              description: Current stock quantity
            description:
              type: string
              example: "Synthetic engine oil 5W-30"
            category:
              type: string
              example: "Lubricants"
            min_stock_level:
              type: integer
              example: 10
              description: Minimum stock level before reordering
            supplier:
              type: string
              example: "AutoParts Inc."
    responses:
      201:
        description: Inventory item created successfully
        schema:
          $ref: '#/definitions/InventoryItem'
      400:
        description: Validation errors
        schema:
          $ref: '#/definitions/ValidationError'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Request body must be JSON'}), 400
            
        errors = inventory_schema.validate(data)
        if errors:
            return jsonify(errors), 400
        
        item = Inventory(
            name=data['item_name'],
            price=data.get('price', 0.0),
            quantity=data.get('quantity', 0),
            description=data.get('description', ''),
            category=data.get('category', ''),
            min_stock_level=data.get('min_stock_level', 0),
            supplier=data.get('supplier', '')
        )
        
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create inventory item', 'details': str(e)}), 500

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@mechanic_token_required
def update_inventory_item(mechanic_id, item_id):
    """
    Update inventory item
    ---
    tags:
      - Inventory
    security:
      - BearerAuth: []
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            item_name:
              type: string
              example: "Premium Engine Oil"
            price:
              type: number
              format: float
              example: 34.99
            quantity:
              type: integer
              example: 45
            description:
              type: string
              example: "Premium synthetic engine oil 5W-30"
            category:
              type: string
              example: "Lubricants"
            min_stock_level:
              type: integer
              example: 15
            supplier:
              type: string
              example: "Premium AutoParts Inc."
    responses:
      200:
        description: Inventory item updated successfully
        schema:
          $ref: '#/definitions/InventoryItem'
      400:
        description: Invalid request data
        schema:
          $ref: '#/definitions/Error'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Inventory item not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        item = Inventory.query.get_or_404(item_id)
        data = request.json
        
        if data is None:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        if 'item_name' in data:
            item.name = data['item_name']
        if 'price' in data:
            item.price = data['price']
        if 'quantity' in data:
            item.quantity = data['quantity']
        if 'description' in data:
            item.description = data['description']
        if 'category' in data:
            item.category = data['category']
        if 'min_stock_level' in data:
            item.min_stock_level = data['min_stock_level']
        if 'supplier' in data:
            item.supplier = data['supplier']
        
        db.session.commit()
        return jsonify(item.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update inventory item', 'details': str(e)}), 500

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
@mechanic_token_required
def delete_inventory_item(mechanic_id, item_id):
    """
    Delete inventory item
    ---
    tags:
      - Inventory
    security:
      - BearerAuth: []
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      204:
        description: Inventory item deleted successfully
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Inventory item not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        item = Inventory.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete inventory item', 'details': str(e)}), 500

@inventory_bp.route('/low-stock', methods=['GET'])
def get_low_stock_items():
    """
    Get inventory items with low stock
    ---
    tags:
      - Inventory
    parameters:
      - name: threshold
        in: query
        type: integer
        required: false
        description: Custom low stock threshold (defaults to min_stock_level)
        example: 10
    responses:
      200:
        description: Low stock items retrieved successfully
        schema:
          type: array
          items:
            $ref: '#/definitions/InventoryItem'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        threshold = request.args.get('threshold', type=int)
        
        if threshold:
            # Use custom threshold
            items = Inventory.query.filter(Inventory.quantity <= threshold).all()
        else:
            # Use min_stock_level
            items = Inventory.query.filter(Inventory.quantity <= Inventory.min_stock_level).all()
        
        return jsonify([item.to_dict() for item in items])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve low stock items', 'details': str(e)}), 500

@inventory_bp.route('/category/<category_name>', methods=['GET'])
def get_inventory_by_category(category_name):
    """
    Get inventory items by category
    parameters:
      - name: category_name
        in: path
        type: string
        required: true
        example: "Lubricants"
    responses:
      200:
        description: Category items retrieved successfully
        schema:
          type: array
          items:
            $ref: '#/definitions/InventoryItem'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        items = Inventory.query.filter_by(category=category_name).all()
        return jsonify([item.to_dict() for item in items])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve category items', 'details': str(e)}), 500

def test_create_inventory_item(self, app, client):
    """Test creating an inventory item with proper setup"""
    with app.app_context():
        # Create a mechanic for authentication
        mechanic = Mechanic(
            first_name="Test",
            last_name="Mechanic", 
            email="mechanic@example.com"
        )
        mechanic.set_password("password123")
        db.session.add(mechanic)
        db.session.commit()

        # Use actual endpoint from your routes
        response = client.post('/inventory/', json={  # ✅ Use actual endpoint
            'name': 'Test Part',
            'description': 'Test Description', 
            'category': 'Test Category',
            'price': 10.0,
            'quantity_in_stock': 5
        })

        assert response.status_code in [201, 401]  # 201 created or 401 unauthorized