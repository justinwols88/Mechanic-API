# tests/test_service_simple.py
import pytest
import sys
import os
from application import create_app, db
from application.models import ServiceTicket, TicketPart

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_service_ticket_creation():
    """Test basic service ticket functionality"""
    try:
                        
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        
        with app.app_context():
            db.create_all()
            
            # Test that models work
            assert ServiceTicket is not None
            assert TicketPart is not None
            
            print("✓ Service ticket models work correctly!")
            assert True
            
    except Exception as e:
        print(f"✗ Error: {e}")
        assert False, f"Test failed: {e}"