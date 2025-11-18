from flask import Blueprint, request, jsonify
from app.services import AuthService
from app.config import SECRET_KEY, JWT_EXPIRATION_HOURS
import jwt
import os
from datetime import datetime, timedelta

# Importar blueprints
from app.routes.proyecto import proyecto_bp
from app.routes.tarea import tarea_bp
from app.routes.dia import dia_bp
from app.routes.usuario import usuario_bp
from app.routes.empleado import empleado_bp

auth_bp = Blueprint('auth', __name__)

def generate_token(user_id: int, remember_me: bool = False) -> str:
    """Genera un JWT con información del usuario
    
    Args:
        user_id: ID del usuario
        remember_me: Si True, token válido por 30 días. Si False, por 24 horas
    """
    # 24 horas si NO marca "Mantener sesión", 30 días (720 horas) si sí
    hours = 720 if remember_me else 24
    expiration = datetime.utcnow() + timedelta(hours=hours)
    
    payload = {
        'identity': str(user_id),
        'iat': datetime.utcnow(),
        'exp': expiration
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra un nuevo usuario"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Campos requeridos: username, email, password'}), 400
    
    usuario, mensaje = AuthService.crear_usuario(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        nombre_completo=data.get('nombre_completo')
    )
    
    if not usuario:
        return jsonify({'error': mensaje}), 400
    
    return jsonify({'message': mensaje, 'usuario': usuario.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autentica un usuario y devuelve token JWT"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Username y password requeridos'}), 400
    
    usuario = AuthService.autenticar_usuario(data['username'], data['password'])
    
    if not usuario:
        return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
    
    # Crear token JWT
    remember_me = data.get('remember_me', False)
    access_token = generate_token(usuario.id, remember_me)
    
    return jsonify({
        'access_token': access_token,
        'usuario': usuario.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Obtiene el usuario actual verificando el token"""
    token = None
    
    # Obtener token del header Authorization
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    
    if not token:
        return jsonify({'error': 'Token requerido'}), 401
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = int(payload['identity'])
        usuario = AuthService.obtener_usuario_por_id(user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify(usuario.to_dict()), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

@auth_bp.route('/me', methods=['PUT'])
def update_profile():
    """Actualiza perfil del usuario"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    
    if not token:
        return jsonify({'error': 'Token requerido'}), 401
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = int(payload['identity'])
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    
    data = request.get_json()
    
    usuario, mensaje = AuthService.actualizar_perfil(
        user_id,
        nombre_completo=data.get('nombre_completo'),
        email=data.get('email'),
        foto_perfil=data.get('foto_perfil'),
        dia_inicio_semana=data.get('dia_inicio_semana')
    )
    
    if not usuario:
        return jsonify({'error': mensaje}), 400
    
    return jsonify({'message': mensaje, 'usuario': usuario.to_dict()}), 200

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Cambia contraseña del usuario"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    
    if not token:
        return jsonify({'error': 'Token requerido'}), 401
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = int(payload['identity'])
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ['password_actual', 'password_nueva']):
        return jsonify({'error': 'Contraseñas requeridas'}), 400
    
    success, mensaje = AuthService.cambiar_password(
        user_id,
        data['password_actual'],
        data['password_nueva']
    )
    
    if not success:
        return jsonify({'error': mensaje}), 400
    
    return jsonify({'message': mensaje}), 200

@auth_bp.route('/horas-reales', methods=['POST'])
def toggle_horas_reales():
    """Activa/desactiva horas reales"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    
    if not token:
        return jsonify({'error': 'Token requerido'}), 401
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = int(payload['identity'])
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    
    data = request.get_json()
    
    success, mensaje = AuthService.activar_horas_reales(
        user_id,
        data.get('activar', False)
    )
    
    if not success:
        return jsonify({'error': mensaje}), 400
    
    return jsonify({'message': mensaje}), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Cierra la sesión del usuario"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    
    if not token:
        return jsonify({'error': 'Token requerido'}), 401
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = int(payload['identity'])
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    
    # El logout simplemente valida que el token es correcto
    # El cliente debe borrar el token del localStorage/cookies
    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200
