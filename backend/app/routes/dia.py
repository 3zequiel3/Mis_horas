from flask import Blueprint, request, jsonify
from app.services.dia_service import DiaService
from app.services.proyecto_service import ProyectoService
from app.models.proyecto_colaborador import ProyectoColaborador
from app.models.dia_colaborador import DiaColaborador
from app.models.empleado import Empleado
from app.decorators import organization_required

dia_bp = Blueprint('dias', __name__)

@dia_bp.route('/mes/<int:proyecto_id>/<int:anio>/<int:mes>', methods=['GET'])
@organization_required
def get_dias_mes(context, proyecto_id, anio, mes):
    """Obtiene días de un mes específico - FASE 1 MULTI-TENANT + CROSS-ORG"""
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
    
    empleado_id = request.args.get('empleado_id', type=int)
    
    # Para proyectos colaborativos NO filtrar días por usuario
    # Los días son compartidos, las tareas son individuales
    dias = DiaService.obtener_dias_mes(proyecto_id, anio, mes, empleado_id)
    
    # Si es proyecto colaborativo, obtener horas desde dias_colaboradores
    if proyecto.tipo_proyecto == 'colaborativo':
        # Obtener horas del colaborador actual desde tabla dias_colaboradores
        dias_ids = [d.id for d in dias]
        horas_colaborador = DiaColaborador.query.filter(
            DiaColaborador.dia_id.in_(dias_ids),
            DiaColaborador.usuario_colaborador_id == context['user_id']
        ).all()
        
        # Crear mapa de horas por día
        horas_por_dia = {
            hc.dia_id: {
                'trabajadas': hc.horas_trabajadas,
                'reales': hc.horas_reales
            }
            for hc in horas_colaborador
        }
        
        # Obtener configuración de horas reales del colaborador
        colaborador = ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            usuario_id=context['user_id'],
            estado='aceptado'
        ).first()
        
        # Verificar si es el propietario
        es_propietario = (proyecto.usuario_id == context['user_id'])
        
        # Actualizar días con horas del colaborador
        dias_response = []
        for dia in dias:
            dia_dict = dia.to_dict()
            
            if dia.id in horas_por_dia:
                # Tiene registro en dias_colaboradores
                dia_dict['horas_trabajadas'] = horas_por_dia[dia.id]['trabajadas']
                dia_dict['horas_reales'] = horas_por_dia[dia.id]['reales']
            elif es_propietario:
                # Propietario sin registro en dias_colaboradores: usar dias.horas_trabajadas
                # (horas previas a la conversión a colaborativo)
                dia_dict['horas_trabajadas'] = dia.horas_trabajadas
                dia_dict['horas_reales'] = dia.horas_reales
            else:
                # Colaborador sin registro: 0 horas
                dia_dict['horas_trabajadas'] = 0
                dia_dict['horas_reales'] = 0
            
            # Agregar flag de si el colaborador tiene horas_reales activas
            dia_dict['horas_reales_activas'] = colaborador.horas_reales_activas if colaborador else False
            dias_response.append(dia_dict)
        
        return jsonify(dias_response), 200
    
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
    
    # Para proyectos colaborativos, devolver las horas del colaborador actual
    # (no las horas base del día que corresponden al propietario)
    from app.services.proyecto_service import ProyectoService
    proyecto = ProyectoService.obtener_proyecto_por_id(dia.proyecto_id)
    
    if proyecto and proyecto.tipo_proyecto == 'colaborativo':
        dia_dict = dia.to_dict()
        
        dc = DiaColaborador.query.filter_by(
            dia_id=dia_id,
            usuario_colaborador_id=context['user_id']
        ).first()
        
        colaborador = ProyectoColaborador.query.filter_by(
            proyecto_id=dia.proyecto_id,
            usuario_id=context['user_id'],
            estado='aceptado'
        ).first()
        es_propietario = (proyecto.usuario_id == context['user_id'])
        
        if dc:
            dia_dict['horas_trabajadas'] = dc.horas_trabajadas
            dia_dict['horas_reales'] = dc.horas_reales
        elif es_propietario:
            dia_dict['horas_trabajadas'] = dia.horas_trabajadas
            dia_dict['horas_reales'] = dia.horas_reales
        else:
            dia_dict['horas_trabajadas'] = 0
            dia_dict['horas_reales'] = 0
        
        dia_dict['horas_reales_activas'] = colaborador.horas_reales_activas if colaborador else False
        return jsonify(dia_dict), 200
    
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
