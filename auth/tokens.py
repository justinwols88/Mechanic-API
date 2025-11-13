from flask_jwt_extended import JWTManager
import pytz

jwt_manager = JWTManager()

import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "your-super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def encode_token(customer_id):
    try:
        payload = {
            'sub': str(customer_id),
            'type': 'customer',
            'exp': datetime.now(pytz.UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.now(pytz.UTC)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        # If using PyJWT >= 2.0.0, it returns a string directly
        if hasattr(token, 'decode'):
            return token.decode('utf-8')
        return token
    except Exception as e:
        print(f"Token encoding error: {e}")
        raise

def encode_mechanic_token(mechanic_id):
    payload = {
        'sub': str(mechanic_id),
        'type': 'mechanic',
        'exp': datetime.now(pytz.UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get('type') != 'customer':
                return jsonify({'message': 'Invalid token type'}), 401
            customer_id = payload.get('sub')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(customer_id, *args, **kwargs)
    return decorated

def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get('type') != 'mechanic':
                return jsonify({'message': 'Invalid token type'}), 401
            mechanic_id = payload.get('sub')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(mechanic_id, *args, **kwargs)
    return decorated