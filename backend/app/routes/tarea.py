from flask import Blueprint, request, jsonify
from app.services.tarea_service import TareaService
from app.services.proyecto_service import ProyectoService
from app.decorators import organization_required

tarea_bp = Blueprint('tareas', __name__)

@tarea_bp.route('/proyecto/<int:proyecto_id>', methods=['GET'])
@organization_required
def get_tareas_proyecto(context, proyecto_id):
    """Obtiene tareas de un proyecto - FASE 1 MULTI-TENANT"""
    # Verificar que el proyecto pertenece a la organización
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    if not proyecto or proyecto.organization_id != context['organization_id']:
        return jsonify({'error': 'Proyecto no encontrado o no pertenece a esta organización'}), 404
    
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    tareas = TareaService.obtener_tareas_proyecto(proyecto_id, mes, anio)
    return jsonify([t.to_dict(incluir_desglose_empleados=True) for t in tareas]), 200

@tarea_bp.route('', methods=['POST'])
@organization_required
def create_tarea(context):
    """Crea una nueva tarea - FASE 1 MULTI-TENANT"""
    data = request.get_json()
    
    if not data or 'titulo' not in data or 'proyecto_id' not in data or 'mes' not in data or 'anio' not in data:
        return jsonify({'error': 'Campos requeridos: titulo, proyecto_id, mes, anio'}), 400
    
    # Verificar que el proyecto pertenece a la organización
    proyecto = ProyectoService.obtener_proyecto_por_id(data['proyecto_id'])
    if not proyecto or proyecto.organization_id != context['organization_id']:
        return jsonify({'error': 'Proyecto no encontrado o no pertenece a esta organización'}), 404
    
    # Si dias_ids es lista vacía, pasarlo como None para que no procese
    dias_ids = data.get('dias_ids')
    if isinstance(dias_ids, list) and len(dias_ids) == 0:
        dias_ids = None
    
    tarea = TareaService.crear_tarea(
        proyecto_id=data['proyecto_id'],
        titulo=data['titulo'],
        mes=data['mes'],
        anio=data['anio'],
        detalle=data.get('detalle', ''),
        que_falta=data.get('que_falta', ''),
        dias_ids=dias_ids,
        usuario_id=context['user_id']
    )
    
    return jsonify(tarea.to_dict(incluir_desglose_empleados=True)), 201

@tarea_bp.route('/<int:tarea_id>', methods=['GET'])
@organization_required
def get_tarea(context, tarea_id):
    """Obtiene una tarea específica - FASE 1 MULTI-TENANT"""
    tarea = TareaService.obtener_tarea_por_id(tarea_id)
    
    if not tarea:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    return jsonify(tarea.to_dict(incluir_desglose_empleados=True)), 200

@tarea_bp.route('/<int:tarea_id>', methods=['PUT'])
@organization_required
def update_tarea(context, tarea_id):
    """Actualiza una tarea - FASE 1 MULTI-TENANT"""
    data = request.get_json()
    
    tarea = TareaService.actualizar_tarea(
        tarea_id=tarea_id,
        titulo=data.get('titulo'),
        detalle=data.get('detalle'),
        que_falta=data.get('que_falta'),
        dias_ids=data.get('dias_ids'),
        usuario_id=context['user_id']  # Pasar user_id para recalcular horas
    )
    
    if not tarea:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    return jsonify(tarea.to_dict(incluir_desglose_empleados=True)), 200

@tarea_bp.route('/<int:tarea_id>', methods=['DELETE'])
@organization_required
def delete_tarea(context, tarea_id):
    """Elimina una tarea - FASE 1 MULTI-TENANT"""
    success = TareaService.eliminar_tarea(tarea_id)
    
    if not success:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    return jsonify({'message': 'Tarea eliminada'}), 200

@tarea_bp.route('/<int:tarea_id>/dia/<int:dia_id>/horas', methods=['PATCH'])
@organization_required
def update_tarea_dia_horas(context, tarea_id, dia_id):
    """Actualiza las horas de un día específico en una tarea - FASE 1 MULTI-TENANT"""
    data = request.get_json()
    
    if not data or 'horas' not in data:
        return jsonify({'error': 'Campo requerido: horas'}), 400
    
    horas_str = data.get('horas')
    
    tarea = TareaService.actualizar_horas_tarea_dia(
        tarea_id=tarea_id,
        dia_id=dia_id,
        horas_str=horas_str,
        usuario_id=context['user_id']
    )
    
    if not tarea:
        return jsonify({'error': 'Tarea o día no encontrado'}), 404
    
    return jsonify(tarea.to_dict()), 200

@tarea_bp.route('/proyecto/<int:proyecto_id>/disponibles/<int:anio>/<int:mes>', methods=['GET'])
@organization_required
def get_dias_disponibles(context, proyecto_id, anio, mes):
    """Obtiene días disponibles para asignar"""
    # Validar que el proyecto pertenece a la organización
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    if not proyecto or proyecto.organization_id != context['organization_id']:
        return jsonify({'error': 'Proyecto no encontrado o no pertenece a la organización'}), 404
    
    tarea_excluir_id = request.args.get('excluir_tarea_id', type=int)
    dias = TareaService.obtener_dias_disponibles(proyecto_id, anio, mes, tarea_excluir_id)
    return jsonify([d.to_dict() for d in dias]), 200
