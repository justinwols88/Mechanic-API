# tests/test_fix_imports.py
import pytest
import sys
import os


# Add the parent directory to the Python path BEFORE any application imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from application import create_app, db

def test_ticketpart_import():
    """Test that TicketPart can be imported successfully"""
    try:
        from application.models import TicketPart
        print("✓ TicketPart import successful!")
        assert True
    except ImportError as e:
        print(f"✗ TicketPart import failed: {e}")
        assert False, f"Import failed: {e}"

def test_service_ticket_routes_import():
    """Test that service ticket routes can be imported without service_inventory"""
    try:
        # This should not raise an ImportError about service_inventory
        from application.blueprints.service_ticket import routes
        print("✓ Service ticket routes import successful!")
        assert True
    except ImportError as e:
        if "service_inventory" in str(e):
            print("✗ service_inventory import still exists!")
            assert False, "service_inventory import still exists in routes"
        else:
            print(f"✗ Other import error: {e}")
            assert False, f"Other import error: {e}"

def test_app_creation():
    """Test that the app can be created without import errors"""
    try:
        app = create_app()
        print("✓ App creation successful!")
        assert app is not None
    except ImportError as e:
        if "service_inventory" in str(e):
            print("✗ service_inventory import preventing app creation!")
            assert False, "service_inventory import preventing app creation"
        else:
            print(f"✗ Other import error during app creation: {e}")
            assert False, f"Other import error: {e}"