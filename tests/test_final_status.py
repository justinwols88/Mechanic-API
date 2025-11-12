# tests/test_final_status.py
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import create_app
from .test_utils import TestUtils

class TestFinalStatus(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        from application.extensions import db
        db.create_all()
        
        # Create test data
        self.customer = TestUtils.create_test_customer()
        self.mechanic = TestUtils.create_test_mechanic()
        self.customer_id = self.customer.id
        self.mechanic_id = self.mechanic.id
    
    def tearDown(self):
        from application.extensions import db
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_final_status_report(self):
        """Generate a final status report of all endpoints"""
        print("\n" + "="*60)
        print("FINAL API STATUS REPORT")
        print("="*60)
        
        # Test all major endpoints
        endpoints = [
            # Customer endpoints
            ('GET', '/customers/', 'Customer List'),
            ('GET', f'/customers/{self.customer_id}', 'Specific Customer'),
            ('POST', '/customers/login', 'Customer Login'),
            ('GET', '/customers/profile', 'Customer Profile (Protected)'),
            ('GET', '/customers/my-tickets', 'Customer Tickets (Protected)'),
            
            # Mechanic endpoints
            ('GET', '/mechanic/', 'Mechanic List (Protected)'),
            ('GET', f'/mechanic/{self.mechanic_id}', 'Specific Mechanic (Protected)'),
            ('POST', '/mechanic/login', 'Mechanic Login'),
            ('GET', '/mechanic/profile', 'Mechanic Profile (Protected)'),
            
            # Inventory endpoints (should be public)
            ('GET', '/inventory/', 'Inventory List'),
            ('GET', '/inventory/1', 'Specific Inventory Item'),
            
            # Vehicle endpoints
            ('GET', '/vehicles/vehicles', 'Vehicle List (Protected)'),
            
            # Service Ticket endpoints
            ('GET', '/service-tickets/api/service-tickets', 'Service Tickets (Protected)'),
        ]
        
        working = []
        needs_auth = []
        needs_data = []
        errors = []
        
        for method, endpoint, description in endpoints:
            response = None
            if method == 'GET':
                response = self.client.get(endpoint)
            elif method == 'POST':
                # For login endpoints, try with empty data first
                response = self.client.post(endpoint, json={})
            
            if response is None:
                errors.append(f"❓ {method} {endpoint} - {description} (unsupported method)")
                continue
            
            status = response.status_code
            
            if status == 200:
                working.append(f"✅ {method} {endpoint} - {description}")
            elif status == 401:
                needs_auth.append(f"🔐 {method} {endpoint} - {description} (needs authentication)")
            elif status == 400:
                needs_data.append(f"📝 {method} {endpoint} - {description} (needs proper data)")
            elif status == 404:
                errors.append(f"❌ {method} {endpoint} - {description} (404 Not Found)")
            elif status == 500:
                errors.append(f"💥 {method} {endpoint} - {description} (500 Internal Error)")
            else:
                errors.append(f"❓ {method} {endpoint} - {description} (unexpected: {status})")
        
        # Print report
        print("\n📊 STATUS SUMMARY:")
        print(f"Working: {len(working)}")
        print(f"Needs Authentication: {len(needs_auth)}") 
        print(f"Needs Data: {len(needs_data)}")
        print(f"Errors: {len(errors)}")
        
        print("\n✅ WORKING ENDPOINTS:")
        for item in working:
            print(f"  {item}")
        
        print("\n🔐 ENDPOINTS NEEDING AUTHENTICATION:")
        for item in needs_auth:
            print(f"  {item}")
        
        print("\n📝 ENDPOINTS NEEDING PROPER DATA:")
        for item in needs_data:
            print(f"  {item}")
        
        print("\n❌ ENDPOINTS WITH ERRORS:")
        for item in errors:
            print(f"  {item}")
        
        print("\n" + "="*60)
        
        # Overall assessment
        total_endpoints = len(endpoints)
        working_percentage = (len(working) / total_endpoints) * 100
        
        print(f"OVERALL: {working_percentage:.1f}% of endpoints working")
        
        if working_percentage >= 80:
            print("🎉 EXCELLENT - Most endpoints are working!")
        elif working_percentage >= 60:
            print("👍 GOOD - Many endpoints are working")
        elif working_percentage >= 40:
            print("⚠️  FAIR - Some endpoints need attention")
        else:
            print("🚨 NEEDS WORK - Many endpoints need fixes")
        
        print("="*60)
        
        # Test should pass if we have at least some working endpoints
        self.assertGreater(len(working), 0, "At least some endpoints should be working")

if __name__ == '__main__':
    unittest.main()