"""
Rutas para gestión de deudas de horas y justificaciones
"""

from flask import Blueprint, request, jsonify
from app.decorators import token_required
from app.utils.response import success_response, error_response
from app.models import Empleado, Proyecto, DeudaHoras, Justificacion, ConfiguracionAsistencia, Notificacion, Usuario
from app.services.email_service import EmailService
from app import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

deuda_bp = Blueprint('deudas', __name__, url_prefix='/api/deudas')


@deuda_bp.route('/empleado', methods=['GET'])
@token_required
def obtener_deudas_empleado(usuario_actual):
    """
    Obtiene las deudas de un empleado
    Query params:
        - empleado_id: ID del empleado (requerido)
        - proyecto_id: ID del proyecto (requerido)
        - estado: activa, justificada, compensada, cerrada (opcional)
    """
    try:
        empleado_id = request.args.get('empleado_id', type=int)
        proyecto_id = request.args.get('proyecto_id', type=int)
        estado = request.args.get('estado')
        
        if not all([empleado_id, proyecto_id]):
            return error_response('empleado_id y proyecto_id son requeridos', 400)
        
        # Verificar permisos
        empleado = Empleado.query.get(empleado_id)
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not empleado or not proyecto:
            return error_response('Empleado o proyecto no encontrado', 404)
        
        if empleado.usuario_id != usuario_actual['id'] and proyecto.usuario_id != usuario_actual['id']:
            return error_response('No tienes permisos para ver las deudas de este empleado', 403)
        
        # Obtener deudas
        query = DeudaHoras.query.filter_by(
            empleado_id=empleado_id,
            proyecto_id=proyecto_id
        )
        
        if estado:
            query = query.filter_by(estado=estado)
        
        deudas = query.order_by(DeudaHoras.fecha_inicio.desc()).all()
        
        # Calcular totales
        total_deudas = sum(float(d.horas_debidas or 0) for d in deudas)
        total_justificadas = sum(float(d.horas_justificadas or 0) for d in deudas)
        total_compensadas = sum(float(d.horas_compensadas or 0) for d in deudas)
        total_pendientes = sum(d.horas_pendientes for d in deudas)
        
        return success_response(
            data={
                'deudas': [d.to_dict() for d in deudas],
                'resumen': {
                    'total_deudas': total_deudas,
                    'total_justificadas': total_justificadas,
                    'total_compensadas': total_compensadas,
                    'total_pendientes': total_pendientes
                }
            },
            message=f'Se encontraron {len(deudas)} registros de deudas'
        )
        
    except Exception as e:
        return error_response(f'Error al obtener deudas: {str(e)}', 500)


@deuda_bp.route('/<int:deuda_id>', methods=['GET'])
@token_required
def obtener_deuda(usuario_actual, deuda_id):
    """
    Obtiene los detalles de una deuda específica
    """
    try:
        
        deuda = DeudaHoras.query.get(deuda_id)
        
        if not deuda:
            return error_response('Deuda no encontrada', 404)
        
        # Verificar permisos
        empleado = Empleado.query.get(deuda.empleado_id)
        proyecto = Proyecto.query.get(deuda.proyecto_id)
        
        if empleado.usuario_id != usuario_actual['id'] and proyecto.usuario_id != usuario_actual['id']:
            return error_response('No tienes permisos para ver esta deuda', 403)
        
        return success_response(
            data={'deuda': deuda.to_dict()}
        )
        
    except Exception as e:
        return error_response(f'Error al obtener deuda: {str(e)}', 500)


@deuda_bp.route('/<int:deuda_id>/justificar', methods=['POST'])
@token_required
def crear_justificacion(usuario_actual, deuda_id):
    """
    Crea una justificación para una deuda
    Form data:
        - motivo: Motivo de la justificación (requerido)
        - horas_a_justificar: Horas a justificar (requerido)
        - archivo: Archivo adjunto (opcional)
    """
    try:
        
        deuda = DeudaHoras.query.get(deuda_id)
        
        if not deuda:
            return error_response('Deuda no encontrada', 404)
        
        # Verificar que el usuario es el empleado
        empleado = Empleado.query.get(deuda.empleado_id)
        if empleado.usuario_id != usuario_actual['id']:
            return error_response('Solo el empleado puede crear justificaciones', 403)
        
        # Obtener datos del formulario
        motivo = request.form.get('motivo', '').strip()
        horas_a_justificar = request.form.get('horas_a_justificar', type=float)
        
        if not motivo or not horas_a_justificar:
            return error_response('motivo y horas_a_justificar son requeridos', 400)
        
        # Validar que no exceda las horas pendientes
        if horas_a_justificar > deuda.horas_pendientes:
            return error_response(
                f'No puedes justificar más horas de las que debes ({deuda.horas_pendientes} horas)', 
                400
            )
        
        # Verificar límite de justificaciones si está configurado
        config = ConfiguracionAsistencia.query.filter_by(proyecto_id=deuda.proyecto_id).first()
        if config and config.limite_horas_justificables:
            # TODO: Implementar validación de límite según periodo
            pass
        
        # Crear justificación
        justificacion = Justificacion(
            deuda_id=deuda_id,
            empleado_id=deuda.empleado_id,
            proyecto_id=deuda.proyecto_id,
            motivo=motivo,
            horas_a_justificar=horas_a_justificar
        )
        
        # Manejar archivo adjunto si existe
        if 'archivo' in request.files:
            archivo = request.files['archivo']
            if archivo and archivo.filename:
                # Crear directorio de uploads si no existe
                upload_dir = 'uploads/justificaciones'
                os.makedirs(upload_dir, exist_ok=True)
                
                # Guardar archivo con nombre seguro
                filename = secure_filename(archivo.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(upload_dir, unique_filename)
                
                archivo.save(filepath)
                
                justificacion.archivo_url = filepath
                justificacion.archivo_nombre = filename
                justificacion.archivo_tipo = archivo.content_type
                justificacion.archivo_tamano = os.path.getsize(filepath)
        
        db.session.add(justificacion)
        db.session.commit()
        
        # El trigger de la BD creará automáticamente la notificación al admin
        
        return success_response(
            data={'justificacion': justificacion.to_dict()},
            message='Justificación enviada exitosamente. Espera la revisión del administrador.'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error al crear justificación: {str(e)}', 500)


@deuda_bp.route('/justificaciones/<int:justificacion_id>/aprobar', methods=['PUT'])
@token_required
def aprobar_justificacion(usuario_actual, justificacion_id):
    """
    Aprueba una justificación (solo admin)
    Body: { "comentario": "Comentario del admin" } (opcional)
    """
    try:
        
        justificacion = Justificacion.query.get(justificacion_id)
        
        if not justificacion:
            return error_response('Justificación no encontrada', 404)
        
        # Verificar que el usuario es admin del proyecto
        proyecto = Proyecto.query.get(justificacion.proyecto_id)
        if proyecto.usuario_id != usuario_actual['id']:
            return error_response('Solo el administrador del proyecto puede aprobar justificaciones', 403)
        
        if justificacion.estado != 'pendiente':
            return error_response(f'La justificación ya fue {justificacion.estado}', 400)
        
        # Obtener comentario
        data = request.get_json() or {}
        comentario = data.get('comentario')
        
        # Aprobar
        justificacion.aprobar(usuario_actual['id'], comentario)
        
        # Notificar al empleado
        empleado = Empleado.query.get(justificacion.empleado_id)
        
        if empleado.usuario_id:
            notificacion = Notificacion(
                usuario_id=empleado.usuario_id,
                tipo='justificacion_aprobada',
                titulo='✅ Justificación aprobada',
                mensaje=f'Tu justificación de {justificacion.horas_a_justificar} horas ha sido aprobada',
                metadatos={
                    'justificacion_id': justificacion.id,
                    'proyecto_id': proyecto.id,
                    'horas_justificadas': float(justificacion.horas_a_justificar)
                },
                url_accion=f'/proyecto/{proyecto.id}/empleado'
            )
            db.session.add(notificacion)
            db.session.commit()
            
            # Enviar email
            usuario_empleado = Usuario.query.get(empleado.usuario_id)
            if usuario_empleado:
                EmailService.enviar_notificacion_justificacion_aprobada(
                    email_empleado=usuario_empleado.email,
                    nombre_empleado=empleado.nombre,
                    nombre_proyecto=proyecto.nombre,
                    horas_justificadas=float(justificacion.horas_a_justificar),
                    comentario_admin=comentario
                )
        
        return success_response(
            data={'justificacion': justificacion.to_dict()},
            message='Justificación aprobada exitosamente'
        )
        
    except Exception as e:
        return error_response(f'Error al aprobar justificación: {str(e)}', 500)


@deuda_bp.route('/justificaciones/<int:justificacion_id>/rechazar', methods=['PUT'])
@token_required
def rechazar_justificacion(usuario_actual, justificacion_id):
    """
    Rechaza una justificación (solo admin)
    Body: { "comentario": "Motivo del rechazo" } (requerido)
    """
    try:
        
        justificacion = Justificacion.query.get(justificacion_id)
        
        if not justificacion:
            return error_response('Justificación no encontrada', 404)
        
        # Verificar permisos
        proyecto = Proyecto.query.get(justificacion.proyecto_id)
        if proyecto.usuario_id != usuario_actual['id']:
            return error_response('Solo el administrador del proyecto puede rechazar justificaciones', 403)
        
        if justificacion.estado != 'pendiente':
            return error_response(f'La justificación ya fue {justificacion.estado}', 400)
        
        # Obtener comentario (requerido para rechazo)
        data = request.get_json() or {}
        comentario = data.get('comentario', '').strip()
        
        if not comentario:
            return error_response('Debes proporcionar un motivo para el rechazo', 400)
        
        # Rechazar
        justificacion.rechazar(usuario_actual['id'], comentario)
        
        # Notificar al empleado
        empleado = Empleado.query.get(justificacion.empleado_id)
        if empleado.usuario_id:
            notificacion = Notificacion(
                usuario_id=empleado.usuario_id,
                tipo='justificacion_rechazada',
                titulo='❌ Justificación rechazada',
                mensaje=f'Tu justificación de {justificacion.horas_a_justificar} horas fue rechazada',
                metadatos={
                    'justificacion_id': justificacion.id,
                    'proyecto_id': proyecto.id,
                    'comentario': comentario
                },
                url_accion=f'/proyecto/{proyecto.id}/empleado'
            )
            db.session.add(notificacion)
            db.session.commit()
        
        return success_response(
            data={'justificacion': justificacion.to_dict()},
            message='Justificación rechazada'
        )
        
    except Exception as e:
        return error_response(f'Error al rechazar justificación: {str(e)}', 500)


@deuda_bp.route('/justificaciones/proyecto/<int:proyecto_id>', methods=['GET'])
@token_required
def obtener_justificaciones_proyecto(usuario_actual, proyecto_id):
    """
    Obtiene todas las justificaciones de un proyecto (solo admin)
    Query params: estado (opcional): pendiente, aprobada, rechazada
    """
    try:
        
        # Verificar permisos
        proyecto = Proyecto.query.get(proyecto_id)
        if not proyecto or proyecto.usuario_id != usuario_actual['id']:
            return error_response('No tienes permisos para ver las justificaciones de este proyecto', 403)
        
        # Filtrar por estado si se proporciona
        query = Justificacion.query.filter_by(proyecto_id=proyecto_id)
        
        estado = request.args.get('estado')
        if estado:
            query = query.filter_by(estado=estado)
        
        justificaciones = query.order_by(Justificacion.fecha_creacion.desc()).all()
        
        return success_response(
            data={'justificaciones': [j.to_dict() for j in justificaciones]},
            message=f'Se encontraron {len(justificaciones)} justificaciones'
        )
        
    except Exception as e:
        return error_response(f'Error al obtener justificaciones: {str(e)}', 500)


@deuda_bp.route('/justificaciones/empleado', methods=['GET'])
@token_required
def obtener_justificaciones_empleado(usuario_actual):
    """
    Obtiene las justificaciones de un empleado
    Query params:
        - empleado_id: ID del empleado (requerido)
        - proyecto_id: ID del proyecto (requerido)
    """
    try:
        empleado_id = request.args.get('empleado_id', type=int)
        proyecto_id = request.args.get('proyecto_id', type=int)
        
        if not all([empleado_id, proyecto_id]):
            return error_response('empleado_id y proyecto_id son requeridos', 400)
        
        # Verificar permisos
        empleado = Empleado.query.get(empleado_id)
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not empleado or not proyecto:
            return error_response('Empleado o proyecto no encontrado', 404)
        
        if empleado.usuario_id != usuario_actual['id'] and proyecto.usuario_id != usuario_actual['id']:
            return error_response('No tienes permisos para ver estas justificaciones', 403)
        
        justificaciones = Justificacion.query.filter_by(
            empleado_id=empleado_id,
            proyecto_id=proyecto_id
        ).order_by(Justificacion.fecha_creacion.desc()).all()
        
        return success_response(
            data={'justificaciones': [j.to_dict() for j in justificaciones]},
            message=f'Se encontraron {len(justificaciones)} justificaciones'
        )
        
    except Exception as e:
        return error_response(f'Error al obtener justificaciones: {str(e)}', 500)
