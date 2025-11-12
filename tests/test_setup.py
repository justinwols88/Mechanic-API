#!/usr/bin/env python3
"""
Script to verify test setup is working
"""
import sys
import os

# Add application to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    # Test imports
    from application import create_app, db
    from application.models import Customer, Mechanic, Inventory, ServiceTicket, TicketPart
    
    print("✓ All imports successful")
    
    # Test app creation
    app = create_app()
    print("✓ App creation successful")
    
    # Test database operations with test config
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")
        
        # Test basic queries
        customer_count = Customer.query.count()
        print(f"✓ Customer query successful: {customer_count} customers")
        
        # Test creating a customer
        customer = Customer(
            first_name="Test",
            last_name="User", 
        )
        customer.set_password("password123")
        db.session.add(customer)
        db.session.commit()
        print("✓ Customer creation successful")
        
        db.drop_all()
        print("✓ Database cleanup successful")
        
    print("🎉 ALL TESTS PASSED! Your setup is correct.")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()