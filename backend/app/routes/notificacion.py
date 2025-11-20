"""
Rutas para gestión de notificaciones
"""

from flask import Blueprint, request, jsonify
from app.decorators import token_required
from app.services.notificacion_service import NotificacionService
from app.utils.response import success_response, error_response

notificacion_bp = Blueprint('notificaciones', __name__, url_prefix='/api/notificaciones')


@notificacion_bp.route('/', methods=['GET'])
@token_required
def obtener_notificaciones(usuario_actual):
    """
    Obtiene las notificaciones del usuario actual
    Query params:
        - solo_no_leidas: true/false (default: false)
        - limit: número de resultados (default: 50)
        - offset: desplazamiento para paginación (default: 0)
    """
    try:
        solo_no_leidas = request.args.get('solo_no_leidas', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        notificaciones = NotificacionService.obtener_notificaciones_usuario(
            usuario_actual['id'],
            solo_no_leidas,
            limit,
            offset
        )
        
        return success_response(
            data={'notificaciones': notificaciones},
            message=f'Se encontraron {len(notificaciones)} notificaciones'
        )
        
    except Exception as e:
        return error_response(f'Error al obtener notificaciones: {str(e)}', 500)


@notificacion_bp.route('/contador', methods=['GET'])
@token_required
def contar_no_leidas(usuario_actual):
    """
    Cuenta las notificaciones no leídas del usuario
    """
    try:
        count = NotificacionService.contar_no_leidas(usuario_actual['id'])
        
        return success_response(
            data={'no_leidas': count}
        )
        
    except Exception as e:
        return error_response(f'Error al contar notificaciones: {str(e)}', 500)


@notificacion_bp.route('/<int:notificacion_id>/marcar-leida', methods=['PUT'])
@token_required
def marcar_como_leida(usuario_actual, notificacion_id):
    """
    Marca una notificación como leída
    """
    try:
        notificacion, error = NotificacionService.marcar_como_leida(
            notificacion_id,
            usuario_actual['id']
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            data={'notificacion': notificacion.to_dict()},
            message='Notificación marcada como leída'
        )
        
    except Exception as e:
        return error_response(f'Error al marcar notificación: {str(e)}', 500)


@notificacion_bp.route('/marcar-todas-leidas', methods=['PUT'])
@token_required
def marcar_todas_como_leidas(usuario_actual):
    """
    Marca todas las notificaciones del usuario como leídas
    """
    try:
        success, error = NotificacionService.marcar_todas_como_leidas(usuario_actual['id'])
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            message='Todas las notificaciones marcadas como leídas'
        )
        
    except Exception as e:
        return error_response(f'Error al marcar todas como leídas: {str(e)}', 500)


@notificacion_bp.route('/<int:notificacion_id>/archivar', methods=['PUT'])
@token_required
def archivar_notificacion(usuario_actual, notificacion_id):
    """
    Archiva una notificación
    """
    try:
        notificacion, error = NotificacionService.archivar_notificacion(
            notificacion_id,
            usuario_actual['id']
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            data={'notificacion': notificacion.to_dict()},
            message='Notificación archivada'
        )
        
    except Exception as e:
        return error_response(f'Error al archivar notificación: {str(e)}', 500)


@notificacion_bp.route('/<int:notificacion_id>', methods=['DELETE'])
@token_required
def eliminar_notificacion(usuario_actual, notificacion_id):
    """
    Elimina una notificación
    """
    try:
        success, error = NotificacionService.eliminar_notificacion(
            notificacion_id,
            usuario_actual['id']
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            message='Notificación eliminada'
        )
        
    except Exception as e:
        return error_response(f'Error al eliminar notificación: {str(e)}', 500)
