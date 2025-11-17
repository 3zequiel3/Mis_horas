from flask import Blueprint, request, jsonify
from app.services.proyecto_service import ProyectoService
from app.decorators import token_required

proyecto_bp = Blueprint('proyectos', __name__)

# IMPORTANTE: Las rutas más específicas deben ir PRIMERO antes de las rutas parametrizadas

@proyecto_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_estadisticas(user_id):
    """Obtiene estadísticas del usuario"""
    stats = ProyectoService.obtener_estadisticas_usuario(user_id)
    return jsonify(stats), 200

@proyecto_bp.route('', methods=['GET'])
@token_required
def get_proyectos(user_id):
    """Obtiene proyectos del usuario"""
    proyectos = ProyectoService.obtener_proyectos_usuario(user_id)
    return jsonify([p.to_dict() for p in proyectos]), 200

@proyecto_bp.route('', methods=['POST'])
@token_required
def create_proyecto(user_id):
    """Crea un nuevo proyecto"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['nombre', 'anio', 'mes']):
        return jsonify({'error': 'Campos requeridos: nombre, anio, mes'}), 400
    
    proyecto = ProyectoService.crear_proyecto(
        nombre=data['nombre'],
        descripcion=data.get('descripcion', ''),
        anio=data['anio'],
        mes=data['mes'],
        usuario_id=user_id
    )
    
    return jsonify(proyecto.to_dict()), 201

@proyecto_bp.route('/<int:proyecto_id>', methods=['GET'])
@token_required
def get_proyecto(user_id, proyecto_id):
    """Obtiene un proyecto específico"""
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    return jsonify(proyecto.to_dict()), 200

@proyecto_bp.route('/<int:proyecto_id>/meses', methods=['GET'])
@token_required
def get_meses(user_id, proyecto_id):
    """Obtiene meses del proyecto"""
    meses = ProyectoService.obtener_meses_proyecto(proyecto_id)
    return jsonify(meses), 200

@proyecto_bp.route('/<int:proyecto_id>/meses', methods=['POST'])
@token_required
def add_mes(user_id, proyecto_id):
    """Agrega un mes al proyecto"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['anio', 'mes']):
        return jsonify({'error': 'Campos requeridos: anio, mes'}), 400
    
    success = ProyectoService.agregar_mes_proyecto(
        proyecto_id,
        data['anio'],
        data['mes']
    )
    
    if not success:
        return jsonify({'error': 'El mes ya existe o proyecto no encontrado'}), 400
    
    return jsonify({'message': 'Mes agregado exitosamente'}), 201

@proyecto_bp.route('/<int:proyecto_id>/estado', methods=['PUT'])
@token_required
def cambiar_estado(user_id, proyecto_id):
    """Cambia estado del proyecto"""
    data = request.get_json()
    
    if 'activo' not in data:
        return jsonify({'error': 'Campo requerido: activo'}), 400
    
    success = ProyectoService.cambiar_estado_proyecto(proyecto_id, data['activo'])
    
    if not success:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    return jsonify({'message': 'Estado actualizado'}), 200

@proyecto_bp.route('/<int:proyecto_id>', methods=['DELETE'])
@token_required
def delete_proyecto(user_id, proyecto_id):
    """Elimina un proyecto"""
    success = ProyectoService.eliminar_proyecto(proyecto_id)
    
    if not success:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    return jsonify({'message': 'Proyecto eliminado'}), 200
