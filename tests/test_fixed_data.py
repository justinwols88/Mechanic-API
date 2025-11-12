# test_fixed_data.py
from application import create_app, db 

def test_with_correct_data():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.create_all()
        
        client = app.test_client()
        
        # Correct data with item_name instead of name
        correct_item = {
            'item_name': 'Test Air Filter',
            'category': 'filters',
            'quantity': 25,
            'price': 15.99,
            'min_stock_level': 10
        }
        
        print("=== Testing with corrected data ===")
        response = client.post('/inventory/',
                             json=correct_item,
                             content_type='application/json')
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Success! Item created with correct field names")
            # Check the created item
            items = db.session.execute(db.select(db.text("* FROM inventory"))).fetchall()
            print(f"Items in database: {len(items)}")
            for item in items:
                print(f"  - {item}")
        else:
            print(f"Response data: {response.get_data(as_text=True)}")
        
        db.drop_all()

if __name__ == '__main__':
    test_with_correct_data()