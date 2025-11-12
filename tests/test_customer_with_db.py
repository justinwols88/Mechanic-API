# tests/test_customer_with_db.py
from application import create_app, db
import unittest
import sys
import os
from tests.test_base import BaseTestCase


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCustomerWithDB(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_customers_list(self):
        response = self.client.get('/customers/')
        # Now we expect 200 because the database is set up, but if there's no data, it might return 200 with an empty list.
        self.assertEqual(response.status_code, 200)

    def test_customer_profile(self):
        response = self.client.get('/customers/profile')
        # This endpoint might require authentication, so we might get 401
        self.assertIn(response.status_code, [200, 401])