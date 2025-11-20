"""
Rutas para gestión de configuración de asistencia
"""

from flask import Blueprint, request, jsonify
from app.decorators import token_required
from app.utils.response import success_response, error_response
from app.models import Proyecto, ConfiguracionAsistencia, Empleado
from app import db
from datetime import datetime

configuracion_bp = Blueprint('configuracion_asistencia', __name__, url_prefix='/api/configuracion-asistencia')


@configuracion_bp.route('/proyecto/<int:proyecto_id>', methods=['GET'])
@token_required
def obtener_configuracion(usuario_actual, proyecto_id):
    """
    Obtiene la configuración de asistencia de un proyecto
    """
    try:
        
        # Verificar que el proyecto existe y el usuario tiene acceso
        proyecto = Proyecto.query.get(proyecto_id)
        if not proyecto:
            return error_response('Proyecto no encontrado', 404)
        
        # El admin puede ver, y los empleados asociados también
        es_admin = proyecto.usuario_id == usuario_actual['id']
        es_empleado = Empleado.query.filter_by(
            proyecto_id=proyecto_id,
            usuario_id=usuario_actual['id']
        ).first() is not None
        
        if not es_admin and not es_empleado:
            return error_response('No tienes permisos para ver la configuración de este proyecto', 403)
        
        # Buscar o crear configuración
        config = ConfiguracionAsistencia.query.filter_by(proyecto_id=proyecto_id).first()
        
        if not config:
            # Crear configuración por defecto
            config = ConfiguracionAsistencia(proyecto_id=proyecto_id)
            db.session.add(config)
            db.session.commit()
        
        return success_response(
            data={'configuracion': config.to_dict()}
        )
        
    except Exception as e:
        return error_response(f'Error al obtener configuración: {str(e)}', 500)


@configuracion_bp.route('/proyecto/<int:proyecto_id>', methods=['PUT'])
@token_required
def actualizar_configuracion(usuario_actual, proyecto_id):
    """
    Actualiza la configuración de asistencia de un proyecto (solo admin)
    Body: {
        "modo_asistencia_activo": true,
        "politica_horas_extras": "compensar_deuda",
        "tolerancia_retraso_minutos": 15,
        "marcar_salida_automatica": true,
        "permitir_justificaciones": true,
        "requiere_aprobacion_justificaciones": true,
        "limite_horas_justificables": 40,
        "periodo_limite_justificaciones": "mensual",
        "enviar_recordatorio_marcado": true,
        "enviar_alerta_deuda": true,
        "hora_recordatorio_entrada": "09:00",
        "hora_recordatorio_salida": "18:00"
    }
    """
    try:
        
        # Verificar que el usuario es admin del proyecto
        proyecto = Proyecto.query.get(proyecto_id)
        if not proyecto or proyecto.usuario_id != usuario_actual['id']:
            return error_response('No tienes permisos para modificar la configuración de este proyecto', 403)
        
        # Buscar o crear configuración
        config = ConfiguracionAsistencia.query.filter_by(proyecto_id=proyecto_id).first()
        
        if not config:
            config = ConfiguracionAsistencia(proyecto_id=proyecto_id)
            db.session.add(config)
        
        # Actualizar campos
        data = request.get_json()
        
        if 'modo_asistencia_activo' in data:
            config.modo_asistencia_activo = data['modo_asistencia_activo']
        
        if 'politica_horas_extras' in data:
            politica = data['politica_horas_extras']
            if politica not in ['compensar_deuda', 'bloquear_extras', 'separar_cuentas']:
                return error_response('Política de horas extras inválida', 400)
            config.politica_horas_extras = politica
        
        if 'tolerancia_retraso_minutos' in data:
            config.tolerancia_retraso_minutos = data['tolerancia_retraso_minutos']
        
        if 'marcar_salida_automatica' in data:
            config.marcar_salida_automatica = data['marcar_salida_automatica']
        
        if 'permitir_justificaciones' in data:
            config.permitir_justificaciones = data['permitir_justificaciones']
        
        if 'requiere_aprobacion_justificaciones' in data:
            config.requiere_aprobacion_justificaciones = data['requiere_aprobacion_justificaciones']
        
        if 'limite_horas_justificables' in data:
            config.limite_horas_justificables = data['limite_horas_justificables']
        
        if 'periodo_limite_justificaciones' in data:
            periodo = data['periodo_limite_justificaciones']
            if periodo not in ['diario', 'semanal', 'mensual', 'anual']:
                return error_response('Periodo de límite inválido', 400)
            config.periodo_limite_justificaciones = periodo
        
        if 'enviar_recordatorio_marcado' in data:
            config.enviar_recordatorio_marcado = data['enviar_recordatorio_marcado']
        
        if 'enviar_alerta_deuda' in data:
            config.enviar_alerta_deuda = data['enviar_alerta_deuda']
        
        if 'hora_recordatorio_entrada' in data:
            config.hora_recordatorio_entrada = datetime.strptime(
                data['hora_recordatorio_entrada'], '%H:%M'
            ).time()
        
        if 'hora_recordatorio_salida' in data:
            config.hora_recordatorio_salida = datetime.strptime(
                data['hora_recordatorio_salida'], '%H:%M'
            ).time()
        
        db.session.commit()
        
        return success_response(
            data={'configuracion': config.to_dict()},
            message='Configuración actualizada exitosamente'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error al actualizar configuración: {str(e)}', 500)


@configuracion_bp.route('/proyecto/<int:proyecto_id>/activar', methods=['POST'])
@token_required
def activar_modo_asistencia(usuario_actual, proyecto_id):
    """
    Activa el modo de asistencia en un proyecto (solo admin)
    """
    try:
        
        proyecto = Proyecto.query.get(proyecto_id)
        if not proyecto or proyecto.usuario_id != usuario_actual['id']:
            return error_response('No tienes permisos para activar la asistencia en este proyecto', 403)
        
        # Verificar que el proyecto tiene configuración de turnos
        if not proyecto.modo_horarios or proyecto.modo_horarios == 'corrido':
            if not proyecto.horario_inicio or not proyecto.horario_fin:
                return error_response(
                    'Debes configurar los horarios laborales del proyecto antes de activar la asistencia',
                    400
                )
        
        # Buscar o crear configuración
        config = ConfiguracionAsistencia.query.filter_by(proyecto_id=proyecto_id).first()
        
        if not config:
            config = ConfiguracionAsistencia(proyecto_id=proyecto_id)
            db.session.add(config)
        
        config.modo_asistencia_activo = True
        db.session.commit()
        
        return success_response(
            data={'configuracion': config.to_dict()},
            message='Modo de asistencia activado. Los empleados ahora pueden marcar entrada y salida.'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error al activar modo de asistencia: {str(e)}', 500)


@configuracion_bp.route('/proyecto/<int:proyecto_id>/desactivar', methods=['POST'])
@token_required
def desactivar_modo_asistencia(usuario_actual, proyecto_id):
    """
    Desactiva el modo de asistencia en un proyecto (solo admin)
    """
    try:
        
        proyecto = Proyecto.query.get(proyecto_id)
        if not proyecto or proyecto.usuario_id != usuario_actual['id']:
            return error_response('No tienes permisos para desactivar la asistencia en este proyecto', 403)
        
        config = ConfiguracionAsistencia.query.filter_by(proyecto_id=proyecto_id).first()
        
        if not config:
            return error_response('No existe configuración de asistencia para este proyecto', 404)
        
        config.modo_asistencia_activo = False
        db.session.commit()
        
        return success_response(
            data={'configuracion': config.to_dict()},
            message='Modo de asistencia desactivado'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error al desactivar modo de asistencia: {str(e)}', 500)
