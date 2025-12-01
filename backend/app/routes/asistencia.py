"""
Rutas para gestión de marcado de asistencia
"""

from flask import Blueprint, request, jsonify
from app.decorators import token_required
from app.utils.response import success_response, error_response
from app.utils import calcular_horas_extras
from datetime import datetime, date
from app.models import (
    Empleado, Proyecto, MarcadoAsistencia,
    ConfiguracionAsistencia, Dia, Notificacion
)
from app.services.asistencia_service import AsistenciaService
from app import db

asistencia_bp = Blueprint('asistencia', __name__, url_prefix='/api/asistencia')


@asistencia_bp.route('/marcar-entrada', methods=['POST'])
@token_required
def marcar_entrada(usuario_actual):
    """
    Marca la entrada de un empleado
    Body: {
        "empleado_id": 5,
        "proyecto_id": 1,
        "fecha": "2025-11-20" (opcional, default: hoy),
        "hora": "08:30:00" (opcional, default: ahora)
    }
    """
    try:
        data = request.get_json()
        
        empleado_id = data.get('empleado_id')
        proyecto_id = data.get('proyecto_id')
        
        if not all([empleado_id, proyecto_id]):
            return error_response('empleado_id y proyecto_id son requeridos', 400)
        
        # Verificar que el usuario es el empleado o el admin del proyecto
        empleado = Empleado.query.get(empleado_id)
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not empleado or not proyecto:
            return error_response('Empleado o proyecto no encontrado', 404)
        
        # Permisos: debe ser el empleado asociado o el admin del proyecto
        if empleado.usuario_id != usuario_actual['id'] and proyecto.usuario_id != usuario_actual['id']:
            return error_response('No tienes permisos para marcar la asistencia de este empleado', 403)
        
        # Parsear fecha y hora si se proporcionan
        fecha = None
        if data.get('fecha'):
            fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        
        hora = None
        if data.get('hora'):
            hora = datetime.strptime(data['hora'], '%H:%M:%S').time()
        
        # Marcar entrada
        marcado, error = AsistenciaService.marcar_entrada(
            empleado_id=empleado_id,
            proyecto_id=proyecto_id,
            fecha=fecha,
            hora=hora
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            data={'marcado': marcado.to_dict()},
            message='Entrada registrada exitosamente'
        )
        
    except Exception as e:
        return error_response(f'Error al marcar entrada: {str(e)}', 500)


@asistencia_bp.route('/marcar-salida', methods=['POST'])
@token_required
def marcar_salida(usuario_actual):
    """
    Marca la salida de un empleado
    Body: {
        "empleado_id": 5,
        "proyecto_id": 1,
        "fecha": "2025-11-20" (opcional, default: hoy),
        "hora": "17:30:00" (opcional, default: ahora),
        "confirmar_continuidad": false (opcional)
    }
    """
    try:
        data = request.get_json()
        
        empleado_id = data.get('empleado_id')
        proyecto_id = data.get('proyecto_id')
        confirmar_continuidad = data.get('confirmar_continuidad', False)
        
        if not all([empleado_id, proyecto_id]):
            return error_response('empleado_id y proyecto_id son requeridos', 400)
        
        # Verificar permisos
        empleado = Empleado.query.get(empleado_id)
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not empleado or not proyecto:
            return error_response('Empleado o proyecto no encontrado', 404)
        
        if empleado.usuario_id != usuario_actual['id'] and proyecto.usuario_id != usuario_actual['id']:
            return error_response('No tienes permisos para marcar la asistencia de este empleado', 403)
        
        # Parsear fecha y hora
        fecha = None
        if data.get('fecha'):
            fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        
        hora = None
        if data.get('hora'):
            hora = datetime.strptime(data['hora'], '%H:%M:%S').time()
        
        # Marcar salida
        marcado, error = AsistenciaService.marcar_salida(
            empleado_id=empleado_id,
            proyecto_id=proyecto_id,
            fecha=fecha,
            hora=hora,
            confirmar_continuidad=confirmar_continuidad
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            data={'marcado': marcado.to_dict()},
            message='Salida registrada exitosamente'
        )
        
    except Exception as e:
        return error_response(f'Error al marcar salida: {str(e)}', 500)


@asistencia_bp.route('/marcados', methods=['GET'])
@token_required
def obtener_marcados(usuario_actual):
    """
    Obtiene los marcados de un empleado
    Query params:
        - empleado_id: ID del empleado (requerido)
        - proyecto_id: ID del proyecto (requerido)
        - fecha_inicio: YYYY-MM-DD (opcional)
        - fecha_fin: YYYY-MM-DD (opcional)
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
            return error_response('No tienes permisos para ver los marcados de este empleado', 403)
        
        # Parsear fechas
        fecha_inicio = None
        fecha_fin = None
        
        if request.args.get('fecha_inicio'):
            fecha_inicio = datetime.strptime(request.args.get('fecha_inicio'), '%Y-%m-%d').date()
        
        if request.args.get('fecha_fin'):
            fecha_fin = datetime.strptime(request.args.get('fecha_fin'), '%Y-%m-%d').date()
        
        # Obtener marcados
        marcados = AsistenciaService.obtener_marcados_empleado(
            empleado_id=empleado_id,
            proyecto_id=proyecto_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        return success_response(
            data={'marcados': marcados},
            message=f'Se encontraron {len(marcados)} marcados'
        )
        
    except Exception as e:
        return error_response(f'Error al obtener marcados: {str(e)}', 500)


@asistencia_bp.route('/detectar-ausencias', methods=['POST'])
@token_required
def detectar_ausencias(usuario_actual):
    """
    Detecta ausencias en un proyecto para una fecha específica (solo admin)
    Body: {
        "proyecto_id": 1,
        "fecha": "2025-11-20"
    }
    """
    try:
        data = request.get_json()
        
        proyecto_id = data.get('proyecto_id')
        fecha_str = data.get('fecha')
        
        if not all([proyecto_id, fecha_str]):
            return error_response('proyecto_id y fecha son requeridos', 400)
        
        # Verificar que el usuario es admin del proyecto
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto or proyecto.usuario_id != usuario_actual['id']:
            return error_response('No tienes permisos para detectar ausencias en este proyecto', 403)
        
        # Parsear fecha
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        # Detectar ausencias
        AsistenciaService.detectar_ausencias(proyecto_id, fecha)
        
        return success_response(
            message='Detección de ausencias completada'
        )
        
    except Exception as e:
        return error_response(f'Error al detectar ausencias: {str(e)}', 500)


@asistencia_bp.route('/estado-hoy', methods=['GET'])
@token_required
def obtener_estado_hoy(usuario_actual):
    """
    Obtiene el estado de asistencia del día actual para un empleado
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
            return error_response('No tienes permisos para ver el estado de este empleado', 403)
        
        # Buscar marcado de hoy
        hoy = date.today()
        marcado = MarcadoAsistencia.query.filter_by(
            empleado_id=empleado_id,
            proyecto_id=proyecto_id,
            fecha=hoy
        ).first()
        
        if marcado:
            return success_response(
                data={
                    'tiene_marcado': True,
                    'marcado': marcado.to_dict()
                }
            )
        else:
            return success_response(
                data={
                    'tiene_marcado': False,
                    'marcado': None
                }
            )
        
    except Exception as e:
        return error_response(f'Error al obtener estado de hoy: {str(e)}', 500)


@asistencia_bp.route('/marcados/<int:marcado_id>/editar', methods=['PUT'])
@token_required
def editar_marcado(usuario_actual, marcado_id):
    """
    Edita un marcado de asistencia (solo admin)
    Permite corregir horarios si el empleado olvidó marcar entrada/salida
    
    Body: {
        "hora_entrada": "08:30:00" (opcional),
        "hora_salida": "17:30:00" (opcional),
        "observaciones": "Corregido por olvido del empleado" (opcional)
    }
    """
    try:
        
        marcado = MarcadoAsistencia.query.get(marcado_id)
        
        if not marcado:
            return error_response('Marcado no encontrado', 404)
        
        # Verificar que el usuario es admin del proyecto
        proyecto = Proyecto.query.get(marcado.proyecto_id)
        if not proyecto or proyecto.usuario_id != usuario_actual['id']:
            return error_response('Solo el administrador del proyecto puede editar marcados', 403)
        
        data = request.get_json()
        
        # Guardar valores anteriores para auditoría
        hora_entrada_anterior = marcado.hora_entrada.strftime('%H:%M:%S') if marcado.hora_entrada else None
        hora_salida_anterior = marcado.hora_salida.strftime('%H:%M:%S') if marcado.hora_salida else None
        
        cambios = []
        
        # Actualizar hora de entrada
        if 'hora_entrada' in data and data['hora_entrada']:
            nueva_hora = datetime.strptime(data['hora_entrada'], '%H:%M:%S').time()
            marcado.hora_entrada = nueva_hora
            cambios.append(f"Entrada: {hora_entrada_anterior or 'N/A'} → {nueva_hora.strftime('%H:%M:%S')}")
        
        # Actualizar hora de salida
        if 'hora_salida' in data and data['hora_salida']:
            nueva_hora = datetime.strptime(data['hora_salida'], '%H:%M:%S').time()
            marcado.hora_salida = nueva_hora
            cambios.append(f"Salida: {hora_salida_anterior or 'N/A'} → {nueva_hora.strftime('%H:%M:%S')}")
        
        # Recalcular horas si hay cambios
        if cambios:
            if marcado.hora_entrada and marcado.hora_salida:
                horas_trabajadas = marcado.calcular_horas_trabajadas()
                marcado.horas_trabajadas = horas_trabajadas
                
                # Recalcular horas extras
                config = ConfiguracionAsistencia.query.filter_by(proyecto_id=marcado.proyecto_id).first()
                
                if config:
                    horas_normales, horas_extras = calcular_horas_extras(
                        horas_trabajadas, proyecto, marcado.turno
                    )
                    marcado.horas_normales = horas_normales
                    marcado.horas_extras = horas_extras
                
                # Actualizar tabla dias
                dia = Dia.query.filter_by(
                    proyecto_id=marcado.proyecto_id,
                    empleado_id=marcado.empleado_id,
                    fecha=marcado.fecha
                ).first()
                
                if dia:
                    dia.horas_trabajadas = float(horas_trabajadas)
                    dia.horas_reales = float(horas_trabajadas)
                    dia.hora_entrada = marcado.hora_entrada
                    dia.hora_salida = marcado.hora_salida
                    dia.horas_extras = float(marcado.horas_extras)
        
        # Agregar observaciones
        observacion_admin = data.get('observaciones', '').strip()
        fecha_edicion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        admin_username = usuario_actual.get('username', 'Admin')
        
        nueva_observacion = f"\n[Editado por {admin_username} el {fecha_edicion}]\n"
        nueva_observacion += f"Cambios: {', '.join(cambios)}\n"
        if observacion_admin:
            nueva_observacion += f"Motivo: {observacion_admin}\n"
        
        marcado.observaciones = (marcado.observaciones or '') + nueva_observacion
        
        db.session.commit()
        
        # Notificar al empleado
        empleado = Empleado.query.get(marcado.empleado_id)
        if empleado.usuario_id:
            notificacion = Notificacion(
                usuario_id=empleado.usuario_id,
                tipo='marcado_editado',
                titulo='📝 Marcado corregido',
                mensaje=f'El administrador ha corregido tu marcado del {marcado.fecha.strftime("%d/%m/%Y")}',
                metadatos={
                    'marcado_id': marcado.id,
                    'proyecto_id': proyecto.id,
                    'cambios': cambios
                },
                url_accion=f'/proyecto/{proyecto.id}/empleado'
            )
            db.session.add(notificacion)
            db.session.commit()
        
        return success_response(
            data={'marcado': marcado.to_dict()},
            message='Marcado editado exitosamente'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error al editar marcado: {str(e)}', 500)


@asistencia_bp.route('/marcados/<int:marcado_id>/confirmar-horas-extras', methods=['PUT'])
@token_required
def confirmar_horas_extras(usuario_actual, marcado_id):
    """
    Confirma las horas extras trabajadas después del horario de cierre (solo admin)
    
    Body: {
        "confirmada": true/false,
        "observaciones": "Comentario del admin" (opcional)
    }
    """
    try:
        
        marcado = MarcadoAsistencia.query.get(marcado_id)
        
        if not marcado:
            return error_response('Marcado no encontrado', 404)
        
        # Verificar permisos
        proyecto = Proyecto.query.get(marcado.proyecto_id)
        if not proyecto or proyecto.usuario_id != usuario_actual['id']:
            return error_response('Solo el administrador del proyecto puede confirmar horas extras', 403)
        
        data = request.get_json()
        confirmada = data.get('confirmada', False)
        observaciones = data.get('observaciones', '').strip()
        
        marcado.confirmada_por_admin = confirmada
        
        # Agregar observación
        fecha_confirmacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        admin_username = usuario_actual.get('username', 'Admin')
        
        nueva_obs = f"\n[Horas extras {'confirmadas' if confirmada else 'rechazadas'} por {admin_username} el {fecha_confirmacion}]\n"
        if observaciones:
            nueva_obs += f"Comentario: {observaciones}\n"
        
        marcado.observaciones = (marcado.observaciones or '') + nueva_obs
        
        # Si se rechazan las horas extras, ajustar el cálculo
        if not confirmada and marcado.confirmacion_continua:
            # Las horas después del cierre no cuentan como extras
            config = ConfiguracionAsistencia.query.filter_by(proyecto_id=marcado.proyecto_id).first()
            
            if config:
                # Marcar que las horas extras fueron rechazadas
                marcado.horas_extras = 0
                
                # Actualizar dia
                dia = Dia.query.filter_by(
                    proyecto_id=marcado.proyecto_id,
                    empleado_id=marcado.empleado_id,
                    fecha=marcado.fecha
                ).first()
                
                if dia:
                    dia.horas_extras = 0
        
        db.session.commit()
        
        # Notificar al empleado
        empleado = Empleado.query.get(marcado.empleado_id)
        if empleado.usuario_id:
            notificacion = Notificacion(
                usuario_id=empleado.usuario_id,
                tipo='horas_extras_confirmadas' if confirmada else 'horas_extras_rechazadas',
                titulo=f"{'✅' if confirmada else '❌'} Horas extras {'confirmadas' if confirmada else 'rechazadas'}",
                mensaje=f"El administrador ha {'confirmado' if confirmada else 'rechazado'} tus horas extras del {marcado.fecha.strftime('%d/%m/%Y')}",
                metadatos={
                    'marcado_id': marcado.id,
                    'proyecto_id': proyecto.id,
                    'observaciones': observaciones
                },
                url_accion=f'/proyecto/{proyecto.id}/empleado'
            )
            db.session.add(notificacion)
            db.session.commit()
        
        return success_response(
            data={'marcado': marcado.to_dict()},
            message=f"Horas extras {'confirmadas' if confirmada else 'rechazadas'} exitosamente"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error al confirmar horas extras: {str(e)}', 500)
