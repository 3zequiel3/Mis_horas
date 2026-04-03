from flask import Blueprint, request, jsonify
from app.services.tarea_service import TareaService
from app.services.proyecto_service import ProyectoService
from app.models.proyecto_colaborador import ProyectoColaborador
from app.models.empleado import Empleado
from app.decorators import organization_required

tarea_bp = Blueprint('tareas', __name__)

@tarea_bp.route('/proyecto/<int:proyecto_id>', methods=['GET'])
@organization_required
def get_tareas_proyecto(context, proyecto_id):
    """Obtiene tareas de un proyecto - FASE 1 MULTI-TENANT + CROSS-ORG"""
    # Verificar que el proyecto existe
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    # Verificar acceso: admin, empleado o colaborador cross-org
    es_admin = proyecto.usuario_id == context['user_id']
    es_empleado = Empleado.query.filter_by(
        proyecto_id=proyecto_id,
        usuario_id=context['user_id']
    ).first() is not None
    
    es_colaborador = ProyectoColaborador.query.filter_by(
        proyecto_id=proyecto_id,
        usuario_id=context['user_id'],
        estado='aceptado'
    ).first() is not None
    
    # Validar acceso según organización
    if proyecto.organization_id == context['organization_id']:
        # Misma organización: admin, empleado o colaborador
        if not (es_admin or es_empleado or es_colaborador):
            return jsonify({'error': 'No tienes acceso a este proyecto'}), 403
    else:
        # Diferente organización: solo colaboradores
        if not es_colaborador:
            return jsonify({'error': 'No tienes acceso a este proyecto'}), 403
    
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    
    # Si es proyecto colaborativo, filtrar por el usuario actual
    usuario_colaborador_id = None
    es_propietario = False
    if proyecto.tipo_proyecto == 'colaborativo':
        usuario_colaborador_id = context['user_id']
        es_propietario = (proyecto.usuario_id == context['user_id'])
    
    tareas = TareaService.obtener_tareas_proyecto(proyecto_id, mes, anio, usuario_colaborador_id, es_propietario)
    return jsonify([t.to_dict(incluir_desglose_empleados=True) for t in tareas]), 200

@tarea_bp.route('', methods=['POST'])
@organization_required
def create_tarea(context):
    """Crea una nueva tarea - FASE 1 MULTI-TENANT + CROSS-ORG"""
    data = request.get_json()
    
    if not data or 'titulo' not in data or 'proyecto_id' not in data or 'mes' not in data or 'anio' not in data:
        return jsonify({'error': 'Campos requeridos: titulo, proyecto_id, mes, anio'}), 400
    
    # Verificar que el proyecto existe
    proyecto = ProyectoService.obtener_proyecto_por_id(data['proyecto_id'])
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    # Verificar acceso: admin, empleado o colaborador cross-org
    es_admin = proyecto.usuario_id == context['user_id']
    es_empleado = Empleado.query.filter_by(
        proyecto_id=data['proyecto_id'],
        usuario_id=context['user_id']
    ).first() is not None
    
    es_colaborador = ProyectoColaborador.query.filter_by(
        proyecto_id=data['proyecto_id'],
        usuario_id=context['user_id'],
        estado='aceptado'
    ).first() is not None
    
    # Validar acceso según organización
    if proyecto.organization_id == context['organization_id']:
        # Misma organización: admin, empleado o colaborador
        if not (es_admin or es_empleado or es_colaborador):
            return jsonify({'error': 'No tienes acceso a este proyecto'}), 403
    else:
        # Diferente organización: solo colaboradores
        if not es_colaborador:
            return jsonify({'error': 'No tienes acceso a este proyecto'}), 403
    
    # Si dias_ids es lista vacía, pasarlo como None para que no procese
    dias_ids = data.get('dias_ids')
    if isinstance(dias_ids, list) and len(dias_ids) == 0:
        dias_ids = None
    
    # Si es proyecto colaborativo, asignar la tarea al usuario actual
    usuario_colaborador_id = None
    if proyecto.tipo_proyecto == 'colaborativo':
        usuario_colaborador_id = context['user_id']
    
    tarea = TareaService.crear_tarea(
        proyecto_id=data['proyecto_id'],
        titulo=data['titulo'],
        mes=data['mes'],
        anio=data['anio'],
        detalle=data.get('detalle', ''),
        que_falta=data.get('que_falta', ''),
        dias_ids=dias_ids,
        usuario_id=context['user_id'],
        usuario_colaborador_id=usuario_colaborador_id,
        position=data.get('position')
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
    
    # Para colaborativos recalcular con el contexto correcto del usuario
    proyecto = ProyectoService.obtener_proyecto_por_id(tarea.proyecto_id)
    if proyecto and proyecto.tipo_proyecto == 'colaborativo':
        tarea.horas = TareaService.calcular_horas_tarea(tarea, context['user_id'])
        from app import db
        db.session.commit()
    
    return jsonify(tarea.to_dict(incluir_desglose_empleados=True)), 200

@tarea_bp.route('/<int:tarea_id>', methods=['DELETE'])
@organization_required
def delete_tarea(context, tarea_id):
    """Elimina una tarea - FASE 1 MULTI-TENANT"""
    success = TareaService.eliminar_tarea(tarea_id)
    
    if not success:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    return jsonify({'message': 'Tarea eliminada'}), 200

@tarea_bp.route('/reorder', methods=['PATCH'])
@organization_required
def reorder_tareas(context):
    """Reordena tareas en batch dentro de un mismo grupo lógico"""
    data = request.get_json()
    items = data if isinstance(data, list) else (data or {}).get('items')

    if not isinstance(items, list) or len(items) == 0:
        return jsonify({'error': 'Payload inválido. Envia una lista de items con id y position'}), 400

    first_id = items[0].get('id') if isinstance(items[0], dict) else None
    if not first_id:
        return jsonify({'error': 'Payload inválido. El primer item debe incluir id'}), 400

    tarea = TareaService.obtener_tarea_por_id(first_id)
    if not tarea:
        return jsonify({'error': 'Tarea no encontrada'}), 404

    proyecto = ProyectoService.obtener_proyecto_por_id(tarea.proyecto_id)
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404

    # Verificar acceso: admin, empleado o colaborador cross-org
    es_admin = proyecto.usuario_id == context['user_id']
    es_empleado = Empleado.query.filter_by(
        proyecto_id=proyecto.id,
        usuario_id=context['user_id']
    ).first() is not None

    es_colaborador = ProyectoColaborador.query.filter_by(
        proyecto_id=proyecto.id,
        usuario_id=context['user_id'],
        estado='aceptado'
    ).first() is not None

    # Validar acceso según organización
    if proyecto.organization_id == context['organization_id']:
        if not (es_admin or es_empleado or es_colaborador):
            return jsonify({'error': 'No tienes acceso a este proyecto'}), 403
    else:
        if not es_colaborador:
            return jsonify({'error': 'No tienes acceso a este proyecto'}), 403

    try:
        tareas = TareaService.reordenar_tareas(items)
    except LookupError as exc:
        return jsonify({'error': str(exc)}), 404
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    return jsonify([t.to_dict(incluir_desglose_empleados=True) for t in tareas]), 200

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
    """Obtiene días disponibles para asignar - CROSS-ORG"""
    # Verificar que el proyecto existe
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    # Verificar acceso: admin, empleado o colaborador cross-org
    es_admin = proyecto.usuario_id == context['user_id']
    es_empleado = Empleado.query.filter_by(
        proyecto_id=proyecto_id,
        usuario_id=context['user_id']
    ).first() is not None
    
    es_colaborador = ProyectoColaborador.query.filter_by(
        proyecto_id=proyecto_id,
        usuario_id=context['user_id'],
        estado='aceptado'
    ).first() is not None
    
    # Validar acceso según organización
    if proyecto.organization_id == context['organization_id']:
        # Misma organización: admin, empleado o colaborador
        if not (es_admin or es_empleado or es_colaborador):
            return jsonify({'error': 'No tienes acceso a este proyecto'}), 403
    else:
        # Diferente organización: solo colaboradores
        if not es_colaborador:
            return jsonify({'error': 'No tienes acceso a este proyecto'}), 403
    
    tarea_excluir_id = request.args.get('excluir_tarea_id', type=int)
    dias = TareaService.obtener_dias_disponibles(proyecto_id, anio, mes, context['user_id'], tarea_excluir_id)
    return jsonify([d.to_dict() for d in dias]), 200
