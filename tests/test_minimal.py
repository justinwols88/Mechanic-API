from application import create_app, db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Create a minimal app to test database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_minimal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)

with app.app_context():
    db.create_all()
    print("Minimal app works!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)