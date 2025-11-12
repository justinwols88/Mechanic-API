from application import create_app, db
from application.models import db
import unittest

class TestMember(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()
            