import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
from flask import current_app, request, jsonify
from functools import wraps


def encode_token(user_id, user_type='customer'):
    """Encode JWT token with user ID and type"""
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': user_id,
            'type': user_type  # Added user type
        }
        token = jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY', 'fallback-secret-key'),
            algorithm='HS256'
        )
        return token
    except Exception as e:
        return str(e)


def token_required(f):
    """Decorator for any authenticated user"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        payload = verify_token(token)
        if 'error' in payload:
            return jsonify({'message': payload['error']}), 401
        
        request.user_id = payload['sub']
        request.user_type = payload.get('type', 'customer')
        return f(*args, **kwargs)
    return decorated


def mechanic_required(f):
    """Decorator specifically for mechanics"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        payload = verify_token(token)
        if 'error' in payload:
            return jsonify({'message': payload['error']}), 401
        
        if payload.get('type') != 'mechanic':
            return jsonify({'message': 'Mechanic access required!'}), 403
        
        request.user_id = payload['sub']
        request.user_type = 'mechanic'
        return f(*args, **kwargs)
    return decorated


def get_token_from_request():
    """Extract token from request headers"""
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            return auth_header.split(" ")[1]  # Bearer <token>
        except IndexError:
            return None
    return None


def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config.get('SECRET_KEY', 'fallback-secret-key'), algorithms=['HS256'])
        return payload
    except ExpiredSignatureError:
        return {'error': 'Token expired'}
    except InvalidTokenError:
        return {'error': 'Invalid token'}
