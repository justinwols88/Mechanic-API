# run_fixed.py
from app import create_app
from dotenv import load_dotenv
import os
from sqlalchemy import text

load_dotenv()

app = create_app()

@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'app_name': 'Mechanic-API',
        'environment': os.environ.get('FLASK_ENV', 'development')
    }

@app.route('/test-db')
def test_db():
    from application.extensions import db
    from application.models import Customer
    try:
        # Test database connection
        customer_count = Customer.query.count()
        return {
            'database': 'connected',
            'customers_count': customer_count
        }
    except Exception as e:
        return {
            'database': 'error',
            'error': str(e)
        }, 500

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        from application.extensions import db
        try:
            db.create_all()
            print("✓ Database tables created")
        except Exception as e:
            print(f"✗ Database error: {e}")
        
        app.run(debug=True, host='0.0.0.0', port=5000)