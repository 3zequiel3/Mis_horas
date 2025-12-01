from flask import Blueprint, request, jsonify
from app.services.dia_service import DiaService
from app.services.proyecto_service import ProyectoService
from app.decorators import organization_required

dia_bp = Blueprint('dias', __name__)

@dia_bp.route('/mes/<int:proyecto_id>/<int:anio>/<int:mes>', methods=['GET'])
@organization_required
def get_dias_mes(context, proyecto_id, anio, mes):
    """Obtiene días de un mes específico - FASE 1 MULTI-TENANT"""
    # Verificar que el proyecto pertenece a la organización
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    if not proyecto or proyecto.organization_id != context['organization_id']:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    empleado_id = request.args.get('empleado_id', type=int)
    dias = DiaService.obtener_dias_mes(proyecto_id, anio, mes, empleado_id)
    return jsonify([d.to_dict() for d in dias]), 200

@dia_bp.route('/<int:dia_id>', methods=['GET'])
@organization_required
def get_dia(context, dia_id):
    """Obtiene un día específico - FASE 1 MULTI-TENANT"""
    dia = DiaService.obtener_dia_por_id(dia_id)
    
    if not dia:
        return jsonify({'error': 'Día no encontrado'}), 404
    
    return jsonify(dia.to_dict()), 200

@dia_bp.route('/<int:dia_id>/horas', methods=['PUT'])
@organization_required
def update_horas(context, dia_id):
    """Actualiza horas de un día - FASE 1 MULTI-TENANT"""
    data = request.get_json()
    
    if 'horas' not in data:
        return jsonify({'error': 'Campo requerido: horas'}), 400
    
    dia = DiaService.actualizar_horas_dia(dia_id, data['horas'], context['user_id'])
    
    if not dia:
        return jsonify({'error': 'Día no encontrado'}), 404
    
    return jsonify(dia.to_dict()), 200

@dia_bp.route('/<int:dia_id>/horarios', methods=['PUT'])
@organization_required
def update_horarios(context, dia_id):
    """Actualiza hora de entrada y salida de un día - FASE 1 MULTI-TENANT"""
    data = request.get_json()
    
    hora_entrada = data.get('hora_entrada')
    hora_salida = data.get('hora_salida')
    
    if not hora_entrada or not hora_salida:
        return jsonify({'error': 'Campos requeridos: hora_entrada y hora_salida'}), 400
    
    dia = DiaService.actualizar_horarios_dia(dia_id, hora_entrada, hora_salida, context['user_id'])
    
    if not dia:
        return jsonify({'error': 'Día no encontrado'}), 404
    
    return jsonify(dia.to_dict()), 200

@dia_bp.route('/<int:dia_id>/turnos', methods=['PUT'])
@organization_required
def update_turnos(context, dia_id):
    """Actualiza horarios por turnos de un día - FASE 1 MULTI-TENANT"""
    data = request.get_json()
    
    # Obtener datos de turnos
    turno_manana_entrada = data.get('turno_manana_entrada')
    turno_manana_salida = data.get('turno_manana_salida')
    turno_tarde_entrada = data.get('turno_tarde_entrada')
    turno_tarde_salida = data.get('turno_tarde_salida')
    
    dia = DiaService.actualizar_turnos_dia(
        dia_id, 
        turno_manana_entrada, 
        turno_manana_salida,
        turno_tarde_entrada,
        turno_tarde_salida,
        context['user_id']
    )
    
    if not dia:
        return jsonify({'error': 'Día no encontrado'}), 404
    
    return jsonify(dia.to_dict()), 200
