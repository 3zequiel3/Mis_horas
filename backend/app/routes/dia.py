from flask import Blueprint, request, jsonify
from app.services.dia_service import DiaService
from app.decorators import token_required

dia_bp = Blueprint('dias', __name__)

@dia_bp.route('/mes/<int:proyecto_id>/<int:anio>/<int:mes>', methods=['GET'])
@token_required
def get_dias_mes(user_id, proyecto_id, anio, mes):
    """Obtiene días de un mes específico, opcionalmente filtrados por empleado"""
    empleado_id = request.args.get('empleado_id', type=int)
    dias = DiaService.obtener_dias_mes(proyecto_id, anio, mes, empleado_id)
    return jsonify([d.to_dict() for d in dias]), 200

@dia_bp.route('/<int:dia_id>', methods=['GET'])
@token_required
def get_dia(user_id, dia_id):
    """Obtiene un día específico"""
    dia = DiaService.obtener_dia_por_id(dia_id)
    
    if not dia:
        return jsonify({'error': 'Día no encontrado'}), 404
    
    return jsonify(dia.to_dict()), 200

@dia_bp.route('/<int:dia_id>/horas', methods=['PUT'])
@token_required
def update_horas(user_id, dia_id):
    """Actualiza horas de un día"""
    data = request.get_json()
    
    if 'horas' not in data:
        return jsonify({'error': 'Campo requerido: horas'}), 400
    
    dia = DiaService.actualizar_horas_dia(dia_id, data['horas'], user_id)
    
    if not dia:
        return jsonify({'error': 'Día no encontrado'}), 404
    
    return jsonify(dia.to_dict()), 200

@dia_bp.route('/<int:dia_id>/horarios', methods=['PUT'])
@token_required
def update_horarios(user_id, dia_id):
    """Actualiza hora de entrada y salida de un día (calcula horas_trabajadas automáticamente)"""
    data = request.get_json()
    
    hora_entrada = data.get('hora_entrada')
    hora_salida = data.get('hora_salida')
    
    if not hora_entrada or not hora_salida:
        return jsonify({'error': 'Campos requeridos: hora_entrada y hora_salida'}), 400
    
    dia = DiaService.actualizar_horarios_dia(dia_id, hora_entrada, hora_salida, user_id)
    
    if not dia:
        return jsonify({'error': 'Día no encontrado'}), 404
    
    return jsonify(dia.to_dict()), 200

@dia_bp.route('/<int:dia_id>/turnos', methods=['PUT'])
@token_required
def update_turnos(user_id, dia_id):
    """Actualiza horarios por turnos de un día (calcula horas_trabajadas y extras automáticamente)"""
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
        user_id
    )
    
    if not dia:
        return jsonify({'error': 'Día no encontrado'}), 404
    
    return jsonify(dia.to_dict()), 200
