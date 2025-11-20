from flask import request, jsonify
from functools import wraps
from app.config import SECRET_KEY
import jwt

def get_token_from_request():
    """Extrae el token JWT del header Authorization"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return None
    
    return token

def validate_token():
    """Valida el token JWT y retorna el user_id o None"""
    token = get_token_from_request()
    
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = int(payload['identity'])
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorador para validar token JWT"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = validate_token()
        if not user_id:
            return jsonify({'error': 'Token requerido o inválido'}), 401
        
        # Crear objeto usuario_actual con la estructura esperada
        usuario_actual = {'id': user_id}
        
        return f(usuario_actual, *args, **kwargs)
    return decorated_function