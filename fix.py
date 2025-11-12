import tempfile
from application import create_app
from application.extensions import db
from tests.test_utils import TestUtils

def test_login_response_format():
    """Check what format the login endpoint actually returns"""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    client = app.test_client()
    
    with app.app_context():
        db.create_all()
        
        # Create test customer
        customer = TestUtils.create_test_customer()
        db.session.add(customer)
        db.session.commit()
        
        # Test login
        login_data = {
            'email': customer.email,
            'password': 'password123'
        }
        response = client.post('/customers/login', json=login_data)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Data: {response.get_json()}")
        
        # Cleanup
        import os
        os.close(db_fd)
        os.unlink(db_path)

if __name__ == '__main__':
    test_login_response_format()