from flask import Blueprint, request, jsonify
from app.services import AuthService
from app.decorators import token_required

usuario_bp = Blueprint('usuarios', __name__)

@usuario_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_usuario(usuario_actual, user_id):
    """Obtiene información del usuario"""
    usuario = AuthService.obtener_usuario_por_id(user_id)
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify(usuario.to_dict()), 200
