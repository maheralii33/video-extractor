from functools import wraps
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import User
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

def generate_token(user_id):
    """Generate a JWT token for the user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify a JWT token and return the user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def hash_password(password):
    """Hash a password"""
    return generate_password_hash(password)

def verify_password(stored_hash, password):
    """Verify a password against its hash"""
    return check_password_hash(stored_hash, password)

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from cookie
        if 'token' in flask.request.cookies:
            token = flask.request.cookies.get('token')
            
        if not token:
            return {'error': 'Authentication required'}, 401
            
        user_id = verify_token(token)
        if not user_id:
            return {'error': 'Invalid or expired token'}, 401
            
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = flask.request.cookies.get('token')
        if not token:
            return {'error': 'Authentication required'}, 401
            
        user_id = verify_token(token)
        if not user_id:
            return {'error': 'Invalid or expired token'}, 401
            
        # Check if user is admin
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return {'error': 'Admin privileges required'}, 403
            
        return f(*args, **kwargs)
    return decorated
