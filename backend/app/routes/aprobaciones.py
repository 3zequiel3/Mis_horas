"""
Rutas API para Aprobación de Períodos de Tiempo
Sistema de aprobación de hojas de tiempo
"""

from flask import Blueprint, request, jsonify
from app.decorators import token_required, organization_required
from app.services.time_period_service import TimePeriodService
from app.utils.permissions import has_permission, Permission
from app.utils.response import error_response, success_response

aprobaciones_bp = Blueprint('aprobaciones', __name__, url_prefix='/api/aprobaciones')


@aprobaciones_bp.route('/periods', methods=['GET'])
@organization_required
def get_periods(context):
    """
    Obtiene períodos de tiempo
    
    Query params:
    - proyecto_id: ID del proyecto (opcional)
    - empleado_id: ID del empleado (opcional)
    - anio: Año (opcional)
    - mes: Mes (opcional)
    """
    proyecto_id = request.args.get('proyecto_id', type=int)
    empleado_id = request.args.get('empleado_id', type=int)
    anio = request.args.get('anio', type=int)
    mes = request.args.get('mes', type=int)
    
    if empleado_id:
        # Obtener períodos de un empleado específico
        periods = TimePeriodService.get_employee_periods(
            organization_id=context['organization_id'],
            empleado_id=empleado_id,
            anio=anio,
            mes=mes
        )
    elif proyecto_id:
        # Obtener todos los períodos de un proyecto
        periods = TimePeriodService.get_project_periods(
            organization_id=context['organization_id'],
            proyecto_id=proyecto_id,
            anio=anio,
            mes=mes
        )
    else:
        return error_response("Se requiere proyecto_id o empleado_id", 400)
    
    return success_response({'periods': periods})


@aprobaciones_bp.route('/pending', methods=['GET'])
@organization_required
def get_pending_approvals(context):
    """Obtiene períodos pendientes de aprobación"""
    if not has_permission(context['role'], Permission.APPROVE_TIME):
        return error_response("No tienes permiso para ver aprobaciones pendientes", 403)
    
    proyecto_id = request.args.get('proyecto_id', type=int)
    periods = TimePeriodService.get_pending_approvals(context['organization_id'], proyecto_id=proyecto_id)
    
    return success_response({'periods': periods})


@aprobaciones_bp.route('/periods/<int:period_id>', methods=['GET'])
@organization_required
def get_period_details(context, period_id):
    """Obtiene detalles de un período específico"""
    period = TimePeriodService.get_period_details(context['organization_id'], period_id)
    
    if not period:
        return error_response("Período no encontrado", 404)
    
    return success_response({'period': period})


@aprobaciones_bp.route('/periods/<int:period_id>/submit', methods=['POST'])
@organization_required
def submit_period(context, period_id):
    """Envía un período para aprobación"""
    if not has_permission(context['role'], Permission.SUBMIT_TIME_FOR_APPROVAL):
        return error_response("No tienes permiso para enviar períodos", 403)
    
    success, error_msg = TimePeriodService.submit_period_for_approval(
        organization_id=context['organization_id'],
        period_id=period_id,
        user_id=context['user_id'],
        user_email=context.get('email', ''),
        user_role=context['role']
    )
    
    if success:
        return success_response({'message': 'Período enviado para aprobación'})
    
    return error_response(error_msg or "No se pudo enviar el período", 400)


@aprobaciones_bp.route('/periods/<int:period_id>/approve', methods=['POST'])
@organization_required
def approve_period(context, period_id):
    """Aprueba un período"""
    if not has_permission(context['role'], Permission.APPROVE_TIME):
        return error_response("No tienes permiso para aprobar períodos", 403)
    
    data = request.get_json() or {}
    notes = data.get('notes', '')
    
    success, error_msg = TimePeriodService.approve_period(
        organization_id=context['organization_id'],
        period_id=period_id,
        reviewer_id=context['user_id'],
        reviewer_email=context.get('email', ''),
        reviewer_role=context['role'],
        notes=notes
    )
    
    if success:
        return success_response({'message': 'Período aprobado exitosamente'})
    
    return error_response(error_msg or "No se pudo aprobar el período", 400)


@aprobaciones_bp.route('/periods/<int:period_id>/reject', methods=['POST'])
@organization_required
def reject_period(context, period_id):
    """Rechaza un período de tiempo"""
    if not has_permission(context['role'], Permission.REJECT_TIME):
        return error_response("No tienes permiso para rechazar períodos", 403)
    
    data = request.get_json()
    if not data:
        return error_response("Se requiere el cuerpo de la solicitud", 400)
    
    notes = data.get('notes', '').strip()
    
    if not notes or len(notes) < 10:
        return error_response("Las notas de rechazo son obligatorias (mínimo 10 caracteres)", 400)
    
    success, error_msg = TimePeriodService.reject_period(
        organization_id=context['organization_id'],
        period_id=period_id,
        reviewer_id=context['user_id'],
        reviewer_email=context.get('email', ''),
        reviewer_role=context['role'],
        notes=notes
    )
    
    if success:
        return success_response({'message': 'Período rechazado'})
    
    return error_response(error_msg or "No se pudo rechazar el período", 400)


@aprobaciones_bp.route('/periods/<int:period_id>/reopen', methods=['POST'])
@organization_required
def reopen_period(context, period_id):
    """Reabre un período bloqueado (solo Owner/Admin)"""
    if not has_permission(context['role'], Permission.REOPEN_APPROVED_TIME):
        return error_response("No tienes permiso para reabrir períodos bloqueados", 403)
    
    data = request.get_json()
    if not data:
        return error_response("Se requiere el cuerpo de la solicitud", 400)
    
    reason = data.get('reason', '').strip()
    
    if not reason or len(reason) < 10:
        return error_response("La razón de reapertura es obligatoria (mínimo 10 caracteres)", 400)
    
    success, error_msg = TimePeriodService.reopen_period(
        organization_id=context['organization_id'],
        period_id=period_id,
        user_id=context['user_id'],
        user_email=context.get('email', ''),
        user_role=context['role'],
        reason=reason
    )
    
    if success:
        return success_response({'message': 'Período reabierto exitosamente'})
    
    return error_response(error_msg or "No se pudo reabrir el período", 400)


@aprobaciones_bp.route('/periods/<int:period_id>/lock', methods=['POST'])
@organization_required
def lock_period(context, period_id):
    """Bloquea permanentemente un período aprobado"""
    if not has_permission(context['role'], Permission.LOCK_TIME_PERIOD):
        return error_response("No tienes permiso para bloquear períodos", 403)
    
    success, error_msg = TimePeriodService.lock_period(
        organization_id=context['organization_id'],
        period_id=period_id,
        user_id=context['user_id'],
        user_email=context.get('email', ''),
        user_role=context['role']
    )
    
    if success:
        return success_response({'message': 'Período bloqueado permanentemente'})
    
    return error_response(error_msg or "No se pudo bloquear el período", 400)
