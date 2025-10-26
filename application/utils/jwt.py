import jwt
from datetime import datetime, timedelta
from flask import current_app, request, jsonify
from functools import wraps

def encode_token(customer_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(hours=2),
        'iat': datetime.utcnow(),
        'sub': customer_id
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.split(' ')[1]
        if not token:
            return jsonify({'message': 'Token missing!'}), 401
        customer_id = decode_token(token)
        if not customer_id:
            return jsonify({'message': 'Token invalid or expired!'}), 401
        return f(customer_id, *args, **kwargs)
    return decorated
