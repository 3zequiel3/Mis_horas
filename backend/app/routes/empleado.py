from flask import Blueprint, request, jsonify
from app.services.empleado_service import EmpleadoService
from app.services.proyecto_service import ProyectoService
from app.decorators import organization_required

empleado_bp = Blueprint('empleados', __name__)

@empleado_bp.route('/proyecto/<int:proyecto_id>/empleados', methods=['GET'])
@organization_required
def get_empleados(context, proyecto_id):
    """Obtiene todos los empleados de un proyecto - FASE 1 MULTI-TENANT"""
    # Verificar que el proyecto pertenece a la organización
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    if not proyecto or proyecto.organization_id != context['organization_id']:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    empleados = EmpleadoService.obtener_empleados_proyecto(proyecto_id)
    return jsonify([e.to_dict() for e in empleados]), 200

@empleado_bp.route('/proyecto/<int:proyecto_id>/empleados', methods=['POST'])
@organization_required
def add_empleado(context, proyecto_id):
    """Agrega un empleado a un proyecto - FASE 1 MULTI-TENANT"""
    data = request.get_json()
    
    if not data or 'nombre' not in data:
        return jsonify({'error': 'Campo requerido: nombre'}), 400
    
    # Verificar que el proyecto pertenece a la organización
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    if not proyecto or proyecto.organization_id != context['organization_id']:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    empleado = EmpleadoService.agregar_empleado(proyecto_id, data['nombre'])
    
    if not empleado:
        return jsonify({'error': 'Proyecto no encontrado o no es de tipo empleados'}), 400
    
    return jsonify(empleado.to_dict()), 201

@empleado_bp.route('/empleados/<int:empleado_id>', methods=['GET'])
@organization_required
def get_empleado(context, empleado_id):
    """Obtiene un empleado específico - FASE 1 MULTI-TENANT"""
    empleado = EmpleadoService.obtener_empleado_por_id(empleado_id)
    
    if not empleado:
        return jsonify({'error': 'Empleado no encontrado'}), 404
    
    return jsonify(empleado.to_dict()), 200

@empleado_bp.route('/empleados/<int:empleado_id>', methods=['PUT'])
@organization_required
def update_empleado(context, empleado_id):
    """Actualiza un empleado - FASE 1 MULTI-TENANT"""
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
@organization_required
def delete_empleado(context, empleado_id):
    """Elimina un empleado - FASE 1 MULTI-TENANT"""
    success = EmpleadoService.eliminar_empleado(empleado_id)
    
    if not success:
        return jsonify({'error': 'Empleado no encontrado'}), 404
    
    return jsonify({'message': 'Empleado eliminado'}), 200
