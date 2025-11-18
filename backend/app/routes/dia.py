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
