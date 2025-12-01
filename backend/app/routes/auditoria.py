"""
Rutas API para Auditoría
Sistema de logs y trazabilidad
"""

from flask import Blueprint, request, jsonify, send_file
from app.decorators import token_required, organization_required
from app.services.audit_service import AuditService
from app.utils.permissions import has_permission, Permission
from app.utils.response import error_response, success_response
from datetime import datetime, timedelta
import io

auditoria_bp = Blueprint('auditoria', __name__, url_prefix='/api/auditoria')


@auditoria_bp.route('/logs', methods=['GET'])
@organization_required
def get_audit_logs(context):
    """
    Obtiene logs de auditoría con filtros
    
    Query params:
    - action: Filtrar por acción específica
    - category: Filtrar por categoría
    - user_id: Filtrar por usuario
    - resource_type: Filtrar por tipo de recurso
    - severity: Filtrar por severidad
    - start_date: Fecha inicio (YYYY-MM-DD)
    - end_date: Fecha fin (YYYY-MM-DD)
    - page: Número de página
    - per_page: Registros por página
    """
    # Verificar permiso
    if not has_permission(context['role'], Permission.VIEW_AUDIT_LOG):
        return error_response("No tienes permiso para ver logs de auditoría", 403)
    
    # Obtener parámetros de filtro
    filters = {}
    
    if request.args.get('action'):
        filters['action'] = request.args.get('action')
    
    if request.args.get('category'):
        filters['category'] = request.args.get('category')
    
    if request.args.get('user_id'):
        try:
            filters['user_id'] = int(request.args.get('user_id'))
        except ValueError:
            return error_response("user_id debe ser un número", 400)
    
    if request.args.get('resource_type'):
        filters['resource_type'] = request.args.get('resource_type')
    
    if request.args.get('severity'):
        filters['severity'] = request.args.get('severity')
    
    if request.args.get('proyecto_id'):
        try:
            filters['proyecto_id'] = int(request.args.get('proyecto_id'))
        except ValueError:
            return error_response("proyecto_id debe ser un número", 400)
    
    # Fechas
    if request.args.get('start_date'):
        try:
            filters['start_date'] = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        except ValueError:
            return error_response("Formato de start_date inválido. Use YYYY-MM-DD", 400)
    
    if request.args.get('end_date'):
        try:
            filters['end_date'] = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        except ValueError:
            return error_response("Formato de end_date inválido. Use YYYY-MM-DD", 400)
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    if per_page > 200:
        per_page = 200
    
    # Obtener logs
    logs, total = AuditService.get_organization_logs_paginated(
        organization_id=context['organization_id'],
        filters=filters,
        page=page,
        per_page=per_page
    )
    
    return success_response({
        'logs': logs,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page
        }
    })


@auditoria_bp.route('/recent', methods=['GET'])
@organization_required
def get_recent_activity(context):
    """Obtiene actividad reciente de la organización"""
    if not has_permission(context["role"], Permission.VIEW_AUDIT_LOG):
        return error_response("No tienes permiso para ver logs de auditoría", 403)
    
    limit = request.args.get('limit', 20, type=int)
    if limit > 100:
        limit = 100
    
    logs = AuditService.get_recent_activity(
        organization_id=context['organization_id'],
        limit=limit
    )
    
    return success_response({'logs': logs})


@auditoria_bp.route('/users/<int:user_id>', methods=['GET'])
@organization_required
def get_user_activity(context, user_id):
    """Obtiene actividad de un usuario específico"""
    if not has_permission(context["role"], Permission.VIEW_AUDIT_LOG):
        return error_response("No tienes permiso para ver logs de auditoría", 403)
    
    limit = request.args.get('limit', 50, type=int)
    if limit > 200:
        limit = 200
    
    logs = AuditService.get_user_activity(
        organization_id=context['organization_id'],
        user_id=user_id,
        limit=limit
    )
    
    return success_response({'logs': logs})


@auditoria_bp.route('/resources/<string:resource_type>/<int:resource_id>', methods=['GET'])
@organization_required
def get_resource_history(context, resource_type, resource_id):
    """Obtiene historial de cambios de un recurso"""
    if not has_permission(context["role"], Permission.VIEW_AUDIT_LOG):
        return error_response("No tienes permiso para ver logs de auditoría", 403)
    
    logs = AuditService.get_resource_history(
        organization_id=context['organization_id'],
        resource_type=resource_type,
        resource_id=resource_id
    )
    
    return success_response({'logs': logs})


@auditoria_bp.route('/statistics', methods=['GET'])
@organization_required
def get_statistics(context):
    """Obtiene estadísticas de auditoría"""
    if not has_permission(context["role"], Permission.VIEW_AUDIT_LOG):
        return error_response("No tienes permiso para ver logs de auditoría", 403)
    
    # Fechas por defecto: últimos 30 días
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return error_response("Formato de start_date inválido. Use YYYY-MM-DD", 400)
    else:
        start_date = datetime.now() - timedelta(days=30)
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return error_response("Formato de end_date inválido. Use YYYY-MM-DD", 400)
    else:
        end_date = datetime.now()
    
    stats = AuditService.get_audit_statistics(
        organization_id=context['organization_id'],
        start_date=start_date,
        end_date=end_date
    )
    
    return success_response({
        'statistics': stats,
        'period': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
    })


@auditoria_bp.route('/export', methods=['GET'])
@organization_required
def export_logs(context):
    """
    Exporta logs de auditoría
    
    Query params:
    - format: json o csv (default: json)
    - start_date, end_date: Rango de fechas
    - Otros filtros igual que /logs
    """
    if not has_permission(context["role"], Permission.VIEW_AUDIT_LOG):
        return error_response("No tienes permiso para exportar logs de auditoría", 403)
    
    export_format = request.args.get('format', 'json')
    if export_format not in ['json', 'csv']:
        return error_response("Formato debe ser 'json' o 'csv'", 400)
    
    # Filtros
    filters = {}
    
    if request.args.get('action'):
        filters['action'] = request.args.get('action')
    
    if request.args.get('category'):
        filters['category'] = request.args.get('category')
    
    if request.args.get('severity'):
        filters['severity'] = request.args.get('severity')
    
    if request.args.get('start_date'):
        try:
            filters['start_date'] = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        except ValueError:
            return error_response("Formato de start_date inválido", 400)
    
    if request.args.get('end_date'):
        try:
            filters['end_date'] = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        except ValueError:
            return error_response("Formato de end_date inválido", 400)
    
    # Exportar
    content = AuditService.export_logs(
        organization_id=context['organization_id'],
        format=export_format,
        filters=filters
    )
    
    # Crear archivo en memoria
    file_obj = io.BytesIO()
    file_obj.write(content.encode('utf-8'))
    file_obj.seek(0)
    
    # Nombre de archivo con fecha
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"audit_logs_{timestamp}.{export_format}"
    
    mimetype = 'application/json' if export_format == 'json' else 'text/csv'
    
    return send_file(
        file_obj,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )
