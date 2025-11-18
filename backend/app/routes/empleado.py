from flask import Blueprint, request, jsonify
from app.services.empleado_service import EmpleadoService
from app.decorators import token_required

empleado_bp = Blueprint('empleados', __name__)

@empleado_bp.route('/proyecto/<int:proyecto_id>/empleados', methods=['GET'])
@token_required
def get_empleados(user_id, proyecto_id):
    """Obtiene todos los empleados de un proyecto"""
    empleados = EmpleadoService.obtener_empleados_proyecto(proyecto_id)
    return jsonify([e.to_dict() for e in empleados]), 200

@empleado_bp.route('/proyecto/<int:proyecto_id>/empleados', methods=['POST'])
@token_required
def add_empleado(user_id, proyecto_id):
    """Agrega un empleado a un proyecto"""
    data = request.get_json()
    
    if not data or 'nombre' not in data:
        return jsonify({'error': 'Campo requerido: nombre'}), 400
    
    empleado = EmpleadoService.agregar_empleado(proyecto_id, data['nombre'])
    
    if not empleado:
        return jsonify({'error': 'Proyecto no encontrado o no es de tipo empleados'}), 400
    
    return jsonify(empleado.to_dict()), 201

@empleado_bp.route('/empleados/<int:empleado_id>', methods=['GET'])
@token_required
def get_empleado(user_id, empleado_id):
    """Obtiene un empleado específico"""
    empleado = EmpleadoService.obtener_empleado_por_id(empleado_id)
    
    if not empleado:
        return jsonify({'error': 'Empleado no encontrado'}), 404
    
    return jsonify(empleado.to_dict()), 200

@empleado_bp.route('/empleados/<int:empleado_id>', methods=['PUT'])
@token_required
def update_empleado(user_id, empleado_id):
    """Actualiza un empleado"""
    data = request.get_json()
    
    success = EmpleadoService.actualizar_empleado(
        empleado_id,
        nombre=data.get('nombre'),
        activo=data.get('activo')
    )
    
    if not success:
        return jsonify({'error': 'Empleado no encontrado'}), 404
    
    return jsonify({'message': 'Empleado actualizado'}), 200

@empleado_bp.route('/empleados/<int:empleado_id>', methods=['DELETE'])
@token_required
def delete_empleado(user_id, empleado_id):
    """Elimina un empleado"""
    success = EmpleadoService.eliminar_empleado(empleado_id)
    
    if not success:
        return jsonify({'error': 'Empleado no encontrado'}), 404
    
    return jsonify({'message': 'Empleado eliminado'}), 200
