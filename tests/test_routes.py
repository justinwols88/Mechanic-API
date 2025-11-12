from application import create_app, db
import pytest

def test_service_tickets_routes_exist(app):
    """Test that service tickets routes are registered"""
    with app.app_context():
        # Check if routes exist
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        service_ticket_routes = [rule for rule in rules if 'service-tickets' in rule]
        
        print("Found service ticket routes:", service_ticket_routes)
        
        # Should find at least the base route
        assert any('/api/service-tickets' in rule for rule in rules), \
            f"Service tickets routes not found. Available routes: {rules}"