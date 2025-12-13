"""
Modul JWT Handler
Mengelola pembuatan dan verifikasi JSON Web Tokens untuk autentikasi
"""

import jwt
from datetime import datetime, timedelta
from app.config import get_config

config = get_config()


def create_access_token(user_data):
    """
    Membuat access token JWT untuk user
    
    Args:
        user_data: Dictionary berisi informasi user (sub, username, email, role, dll)
    
    Returns:
        str: Access token JWT yang sudah di-encode
    """
    payload = {
        'sub': user_data['sub'],
        'username': user_data['username'],
        'email': user_data['email'],
        'role': user_data['role'],
        'permissions': user_data['permissions'],
        'factory_id': user_data.get('factory_id'),
        'department': user_data.get('department'),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES),
        'iss': 'gonsters-backend-api',
        'aud': 'gonsters-dashboard',
        'type': 'access'
    }
    
    token = jwt.encode(
        payload,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )
    
    return token


def create_refresh_token(user_id):
    """
    Membuat refresh token JWT untuk user
    
    Args:
        user_id: ID user
    
    Returns:
        str: Refresh token JWT yang sudah di-encode
    """
    payload = {
        'sub': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=config.JWT_REFRESH_TOKEN_EXPIRES),
        'iss': 'gonsters-backend-api',
        'aud': 'gonsters-dashboard',
        'type': 'refresh'
    }
    
    token = jwt.encode(
        payload,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )
    
    return token


def verify_token(token, token_type='access'):
    """
    Verifikasi dan decode JWT token
    
    Args:
        token: JWT token string
        token_type: Tipe token ('access' atau 'refresh')
    
    Returns:
        dict: Payload token jika valid, None jika invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM],
            audience='gonsters-dashboard',
            issuer='gonsters-backend-api'
        )
        
        if payload.get('type') != token_type:
            return None
        
        return payload
    
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def decode_token(token):
    """
    Decode token tanpa verifikasi signature (untuk debugging)
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Payload token jika bisa di-decode, None jika gagal
    """
    try:
        payload = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        return payload
    except Exception:
        return None
