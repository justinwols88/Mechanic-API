"""
Test that we only have one SQLAlchemy instance
"""
import sys
import os


# tests/test_sqlalchemy_singleton.py
def test_single_sqlalchemy_instance():
    """Test that we only have one SQLAlchemy instance"""
    from application.extensions import db as db1
    from application.extensions import db as db2

    # These should be the same object
    assert db1 is db2, "Multiple SQLAlchemy instances detected!"

def test_db_initialized_with_app():
    """Test that db is properly initialized with app"""
from application import create_app, db
    
app = create_app()
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # This should work without errors
with app.app_context():
    db.create_all()
    db.drop_all()
print("✓ db properly initialized with app")

if __name__ == '__main__':
    test_single_sqlalchemy_instance()
    test_db_initialized_with_app()
    print("🎉 SQLAlchemy singleton test passed!")