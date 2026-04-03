from flask import Blueprint, request, jsonify
from app.services.proyecto_service import ProyectoService
from app.decorators import organization_required

proyecto_bp = Blueprint('proyectos', __name__)

# IMPORTANTE: Las rutas más específicas deben ir PRIMERO antes de las rutas parametrizadas

@proyecto_bp.route('/estadisticas', methods=['GET'])
@organization_required
def get_estadisticas(context):
    """Obtiene estadísticas del usuario - FASE 1 MULTI-TENANT"""
    stats = ProyectoService.obtener_estadisticas_usuario(context['user_id'], context['organization_id'])
    return jsonify(stats), 200

@proyecto_bp.route('', methods=['GET'])
@organization_required
def get_proyectos(context):
    """Obtiene proyectos del usuario - FASE 1 MULTI-TENANT"""
    proyectos = ProyectoService.obtener_proyectos_usuario(context['user_id'], context['organization_id'])
    return jsonify([p.to_dict() for p in proyectos]), 200

@proyecto_bp.route('', methods=['POST'])
@organization_required
def create_proyecto(context):
    """Crea un nuevo proyecto - FASE 1 MULTI-TENANT"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['nombre', 'anio', 'mes']):
        return jsonify({'error': 'Campos requeridos: nombre, anio, mes'}), 400
    
    # Validar tipo de proyecto
    tipo_proyecto = data.get('tipo_proyecto', 'personal')
    if tipo_proyecto not in ['personal', 'empleados', 'colaborativo']:
        return jsonify({'error': 'tipo_proyecto debe ser "personal", "empleados" o "colaborativo"'}), 400
    
    # Si es proyecto con empleados, validar que se envíen empleados
    empleados = data.get('empleados', [])
    if tipo_proyecto == 'empleados' and not empleados:
        return jsonify({'error': 'Se requiere al menos un empleado para proyectos con empleados'}), 400
    
    # Validar modo de horarios (opcional, se configura después)
    modo_horarios = data.get('modo_horarios')
    if modo_horarios and modo_horarios not in ['corrido', 'turnos', None]:
        return jsonify({'error': 'modo_horarios debe ser "corrido", "turnos" o null'}), 400
    
    # FASE 1 MULTI-TENANT: Usar context
    # FASE 4: Agregar client_name, brand_color, modules_config, budget
    proyecto = ProyectoService.crear_proyecto(
        nombre=data['nombre'],
        descripcion=data.get('descripcion', ''),
        anio=data['anio'],
        mes=data['mes'],
        usuario_id=context['user_id'],
        organization_id=context['organization_id'],
        tipo_proyecto=tipo_proyecto,
        empleados=empleados,
        horas_reales_activas=data.get('horas_reales_activas', False),
        modo_horarios=modo_horarios,
        horario_inicio=data.get('horario_inicio'),
        horario_fin=data.get('horario_fin'),
        turno_manana_inicio=data.get('turno_manana_inicio'),
        turno_manana_fin=data.get('turno_manana_fin'),
        turno_tarde_inicio=data.get('turno_tarde_inicio'),
        turno_tarde_fin=data.get('turno_tarde_fin'),
        client_name=data.get('client_name'),
        brand_color=data.get('brand_color'),
        modules_config=data.get('modules_config', {
            'budget': False,
            'time_tracking': True,
            'audit': False,
            'public_view': False
        }),
        budget_type=data.get('budget_type', 'none'),
        budget_base_amount=data.get('budget_base_amount'),
        currency=data.get('currency', 'USD')
    )
    
    # Si se crea directamente como colaborativo, registrar al creador como owner
    if tipo_proyecto == 'colaborativo':
        from app.services.colaboradores_service import ColaboradoresService
        ColaboradoresService.convertir_a_colaborativo(proyecto.id, context['user_id'])
    
    return jsonify(proyecto.to_dict()), 201

@proyecto_bp.route('/<int:proyecto_id>', methods=['GET'])
@organization_required
def get_proyecto(context, proyecto_id):
    """Obtiene un proyecto específico - FASE 1 MULTI-TENANT + CROSS-ORG"""
    from app.models.empleado import Empleado
    from app.models.proyecto_colaborador import ProyectoColaborador
    
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    # Verificar acceso: admin, empleado o colaborador
    es_admin = proyecto.usuario_id == context['user_id']
    es_empleado = Empleado.query.filter_by(
        proyecto_id=proyecto_id,
        usuario_id=context['user_id']
    ).first() is not None
    
    # CROSS-ORG: Verificar si es colaborador (permite acceso cross-organization)
    es_colaborador = ProyectoColaborador.query.filter_by(
        proyecto_id=proyecto_id,
        usuario_id=context['user_id'],
        estado='aceptado'
    ).first() is not None
    
    # Si es de la misma organización, validar permisos normales
    # Si es colaborador, permitir acceso cross-organization
    if proyecto.organization_id == context['organization_id']:
        # Misma organización: admin o empleado
        if not (es_admin or es_empleado or es_colaborador):
            return jsonify({'error': 'No tienes acceso a este proyecto'}), 403
    else:
        # Diferente organización: solo colaboradores
        if not es_colaborador:
            return jsonify({'error': 'No tienes acceso a este proyecto'}), 403
    
    return jsonify(proyecto.to_dict()), 200

@proyecto_bp.route('/<int:proyecto_id>', methods=['PUT'])
@organization_required
def update_proyecto(context, proyecto_id):
    """Actualiza un proyecto - FASE 4 UX"""
    from app import db
    
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    # Verificar que el proyecto pertenezca a la organización actual
    if proyecto.organization_id != context['organization_id']:
        return jsonify({'error': 'No tienes acceso a este proyecto'}), 403
    
    # Solo el admin del proyecto puede actualizar
    if proyecto.usuario_id != context['user_id']:
        return jsonify({'error': 'Solo el administrador puede actualizar el proyecto'}), 403
    
    data = request.get_json()
    
    # Actualizar campos permitidos
    if 'nombre' in data:
        proyecto.nombre = data['nombre']
    
    if 'descripcion' in data:
        proyecto.descripcion = data['descripcion']
    
    if 'client_name' in data:
        proyecto.client_name = data['client_name']
    
    if 'brand_color' in data:
        proyecto.brand_color = data['brand_color']
    
    # Actualizar modules_config
    if 'modules_config' in data:
        proyecto.modules_config = data['modules_config']
    
    # Actualizar configuración de presupuesto
    if 'budget_type' in data:
        if data['budget_type'] not in ['none', 'hourly_retainer', 'time_and_materials', 'fixed_price']:
            return jsonify({'error': 'budget_type inválido'}), 400
        proyecto.budget_type = data['budget_type']
    
    if 'budget_base_amount' in data:
        proyecto.budget_base_amount = data['budget_base_amount']
    
    if 'currency' in data:
        proyecto.currency = data['currency']
    
    try:
        db.session.commit()
        return jsonify(proyecto.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar proyecto: {str(e)}'}), 500

@proyecto_bp.route('/<int:proyecto_id>/meses', methods=['GET'])
@organization_required
def get_meses(context, proyecto_id):
    """Obtiene meses del proyecto - FASE 1 MULTI-TENANT"""
    meses = ProyectoService.obtener_meses_proyecto(proyecto_id)
    return jsonify(meses), 200

@proyecto_bp.route('/<int:proyecto_id>/meses', methods=['POST'])
@organization_required
def add_mes(context, proyecto_id):
    """Agrega un mes al proyecto - FASE 1 MULTI-TENANT + COLABORATIVOS
    
    En proyectos colaborativos, los días son globales (compartidos por todos).
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ['anio', 'mes']):
        return jsonify({'error': 'Campos requeridos: anio, mes'}), 400
    
    print(f"[ADD_MES] Creando mes {data['mes']}/{data['anio']} para proyecto {proyecto_id}")
    
    success = ProyectoService.agregar_mes_proyecto(
        proyecto_id,
        data['anio'],
        data['mes']
    )
    
    if not success:
        print(f"[ADD_MES] Error: El mes ya existe o proyecto no encontrado")
        return jsonify({'error': 'El mes ya existe o proyecto no encontrado'}), 400
    
    print(f"[ADD_MES] Mes creado exitosamente")
    return jsonify({'message': 'Mes agregado exitosamente'}), 201

@proyecto_bp.route('/<int:proyecto_id>/estado', methods=['PUT'])
@organization_required
def cambiar_estado(context, proyecto_id):
    """Cambia estado del proyecto - FASE 1 MULTI-TENANT"""
    data = request.get_json()
    
    if 'activo' not in data:
        return jsonify({'error': 'Campo requerido: activo'}), 400
    
    success = ProyectoService.cambiar_estado_proyecto(proyecto_id, data['activo'])
    
    if not success:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    return jsonify({'message': 'Estado actualizado'}), 200

@proyecto_bp.route('/<int:proyecto_id>', methods=['DELETE'])
@organization_required
def delete_proyecto(context, proyecto_id):
    """Elimina un proyecto - FASE 1 MULTI-TENANT"""
    success = ProyectoService.eliminar_proyecto(proyecto_id)
    
    if not success:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    return jsonify({'message': 'Proyecto eliminado'}), 200

@proyecto_bp.route('/<int:proyecto_id>/configuracion', methods=['PUT'])
@organization_required
def update_configuracion(context, proyecto_id):
    """Actualiza configuración del proyecto - FASE 1 MULTI-TENANT"""
    data = request.get_json()
    
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    # Verificar permisos: solo el dueño puede actualizar la configuración
    if proyecto.tipo_proyecto == 'colaborativo':
        from app.models.proyecto_colaborador import ProyectoColaborador
        es_owner = ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            usuario_id=context['user_id'],
            rol='owner',
            estado='aceptado'
        ).first() is not None
        if not es_owner:
            return jsonify({'error': 'Solo el dueño del proyecto puede actualizar la configuración'}), 403
    else:
        if proyecto.usuario_id != context['user_id']:
            return jsonify({'error': 'Solo el dueño del proyecto puede actualizar la configuración'}), 403
    
    from app import db
    from datetime import datetime
    
    # Actualizar configuración básica
    if 'horas_reales_activas' in data:
        proyecto.horas_reales_activas = data['horas_reales_activas']
    
    # Actualizar configuración de turnos
    if 'modo_horarios' in data:
        if data['modo_horarios'] not in ['corrido', 'turnos']:
            return jsonify({'error': 'modo_horarios debe ser "corrido" o "turnos"'}), 400
        proyecto.modo_horarios = data['modo_horarios']
    
    # Actualizar horario laboral (para horas extras)
    if 'horario_inicio' in data:
        if data['horario_inicio']:
            proyecto.horario_inicio = datetime.strptime(data['horario_inicio'], '%H:%M').time()
        else:
            proyecto.horario_inicio = None
    
    if 'horario_fin' in data:
        if data['horario_fin']:
            proyecto.horario_fin = datetime.strptime(data['horario_fin'], '%H:%M').time()
        else:
            proyecto.horario_fin = None
    
    # Actualizar configuración de turnos
    if 'turno_manana_inicio' in data:
        if data['turno_manana_inicio']:
            proyecto.turno_manana_inicio = datetime.strptime(data['turno_manana_inicio'], '%H:%M').time()
        else:
            proyecto.turno_manana_inicio = None
    
    if 'turno_manana_fin' in data:
        if data['turno_manana_fin']:
            proyecto.turno_manana_fin = datetime.strptime(data['turno_manana_fin'], '%H:%M').time()
        else:
            proyecto.turno_manana_fin = None
    
    if 'turno_tarde_inicio' in data:
        if data['turno_tarde_inicio']:
            proyecto.turno_tarde_inicio = datetime.strptime(data['turno_tarde_inicio'], '%H:%M').time()
        else:
            proyecto.turno_tarde_inicio = None
    
    if 'turno_tarde_fin' in data:
        if data['turno_tarde_fin']:
            proyecto.turno_tarde_fin = datetime.strptime(data['turno_tarde_fin'], '%H:%M').time()
        else:
            proyecto.turno_tarde_fin = None
    
    db.session.commit()
    
    return jsonify(proyecto.to_dict()), 200
