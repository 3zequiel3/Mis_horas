from flask import Blueprint, request, jsonify
from app.services.tarea_service import TareaService
from app.decorators import token_required

tarea_bp = Blueprint('tareas', __name__)

@tarea_bp.route('/proyecto/<int:proyecto_id>', methods=['GET'])
@token_required
def get_tareas_proyecto(usuario_actual, proyecto_id):
    """Obtiene tareas de un proyecto"""
    tareas = TareaService.obtener_tareas_proyecto(proyecto_id)
    # Incluir desglose de empleados en la respuesta
    return jsonify([t.to_dict(incluir_desglose_empleados=True) for t in tareas]), 200

@tarea_bp.route('', methods=['POST'])
@token_required
def create_tarea(usuario_actual):
    """Crea una nueva tarea"""
    data = request.get_json()
    
    if not data or 'titulo' not in data or 'proyecto_id' not in data:
        return jsonify({'error': 'Campos requeridos: titulo, proyecto_id'}), 400
    
    # Si dias_ids es lista vacía, pasarlo como None para que no procese
    dias_ids = data.get('dias_ids')
    if isinstance(dias_ids, list) and len(dias_ids) == 0:
        dias_ids = None
    
    tarea = TareaService.crear_tarea(
        proyecto_id=data['proyecto_id'],
        titulo=data['titulo'],
        detalle=data.get('detalle', ''),
        que_falta=data.get('que_falta', ''),
        dias_ids=dias_ids,
        usuario_id=usuario_actual['id']
    )
    
    return jsonify(tarea.to_dict(incluir_desglose_empleados=True)), 201

@tarea_bp.route('/<int:tarea_id>', methods=['GET'])
@token_required
def get_tarea(usuario_actual, tarea_id):
    """Obtiene una tarea específica"""
    tarea = TareaService.obtener_tarea_por_id(tarea_id)
    
    if not tarea:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    return jsonify(tarea.to_dict(incluir_desglose_empleados=True)), 200

@tarea_bp.route('/<int:tarea_id>', methods=['PUT'])
@token_required
def update_tarea(usuario_actual, tarea_id):
    """Actualiza una tarea"""
    data = request.get_json()
    
    tarea = TareaService.actualizar_tarea(
        tarea_id=tarea_id,
        titulo=data.get('titulo'),
        detalle=data.get('detalle'),
        que_falta=data.get('que_falta'),
        dias_ids=data.get('dias_ids'),
        usuario_id=usuario_actual['id']  # Pasar user_id para recalcular horas
    )
    
    if not tarea:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    return jsonify(tarea.to_dict(incluir_desglose_empleados=True)), 200

@tarea_bp.route('/<int:tarea_id>', methods=['DELETE'])
@token_required
def delete_tarea(usuario_actual, tarea_id):
    """Elimina una tarea"""
    success = TareaService.eliminar_tarea(tarea_id)
    
    if not success:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    return jsonify({'message': 'Tarea eliminada'}), 200

@tarea_bp.route('/<int:tarea_id>/dia/<int:dia_id>/horas', methods=['PATCH'])
@token_required
def update_tarea_dia_horas(usuario_actual, tarea_id, dia_id):
    """Actualiza las horas de un día específico en una tarea"""
    data = request.get_json()
    
    if not data or 'horas' not in data:
        return jsonify({'error': 'Campo requerido: horas'}), 400
    
    horas_str = data.get('horas')
    
    tarea = TareaService.actualizar_horas_tarea_dia(
        tarea_id=tarea_id,
        dia_id=dia_id,
        horas_str=horas_str,
        usuario_id=usuario_actual['id']
    )
    
    if not tarea:
        return jsonify({'error': 'Tarea o día no encontrado'}), 404
    
    return jsonify(tarea.to_dict()), 200

@tarea_bp.route('/proyecto/<int:proyecto_id>/disponibles/<int:anio>/<int:mes>', methods=['GET'])
@token_required
def get_dias_disponibles(usuario_actual, proyecto_id, anio, mes):
    """Obtiene días disponibles para asignar"""
    tarea_excluir_id = request.args.get('excluir_tarea_id', type=int)
    dias = TareaService.obtener_dias_disponibles(proyecto_id, anio, mes, tarea_excluir_id)
    return jsonify([d.to_dict() for d in dias]), 200
