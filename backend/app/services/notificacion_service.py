"""
Servicio para gestión de notificaciones
"""

from app import db
from app.models import Notificacion, Usuario
from datetime import datetime, timezone, timedelta
from typing import List, Optional

LOCAL_TZ = timezone(timedelta(hours=-3))


class NotificacionService:
    """Servicio para manejar notificaciones del sistema"""
    
    @staticmethod
    def crear_notificacion(
        usuario_id: int,
        tipo: str,
        titulo: str,
        mensaje: str,
        metadatos: dict = None,
        url_accion: str = None
    ):
        """
        Crea una nueva notificación
        
        Args:
            usuario_id: ID del usuario destinatario
            tipo: Tipo de notificación
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            metadatos: Datos adicionales en formato dict
            url_accion: URL de acción asociada
        
        Returns:
            Notificación creada
        """
        try:
            notificacion = Notificacion(
                usuario_id=usuario_id,
                tipo=tipo,
                titulo=titulo,
                mensaje=mensaje,
                url_accion=url_accion
            )
            
            if metadatos:
                notificacion.metadatos = metadatos
            
            db.session.add(notificacion)
            db.session.commit()
            
            return notificacion
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear notificación: {str(e)}")
            return None
    
    @staticmethod
    def obtener_notificaciones_usuario(
        usuario_id: int,
        solo_no_leidas: bool = False,
        limit: int = 50,
        offset: int = 0
    ):
        """
        Obtiene las notificaciones de un usuario
        
        Args:
            usuario_id: ID del usuario
            solo_no_leidas: Filtrar solo las no leídas
            limit: Cantidad máxima de resultados
            offset: Desplazamiento para paginación
        
        Returns:
            Lista de notificaciones
        """
        query = Notificacion.query.filter_by(usuario_id=usuario_id, archivada=False)
        
        if solo_no_leidas:
            query = query.filter_by(leida=False)
        
        notificaciones = query.order_by(
            Notificacion.fecha_creacion.desc()
        ).limit(limit).offset(offset).all()
        
        return [n.to_dict() for n in notificaciones]
    
    @staticmethod
    def contar_no_leidas(usuario_id: int):
        """Cuenta las notificaciones no leídas de un usuario"""
        count = Notificacion.query.filter_by(
            usuario_id=usuario_id,
            leida=False,
            archivada=False
        ).count()
        
        return count
    
    @staticmethod
    def marcar_como_leida(notificacion_id: int, usuario_id: int):
        """Marca una notificación como leída"""
        try:
            notificacion = Notificacion.query.filter_by(
                id=notificacion_id,
                usuario_id=usuario_id
            ).first()
            
            if not notificacion:
                return None, "Notificación no encontrada"
            
            notificacion.marcar_como_leida()
            
            return notificacion, None
            
        except Exception as e:
            print(f"Error al marcar notificación como leída: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def marcar_todas_como_leidas(usuario_id: int):
        """Marca todas las notificaciones de un usuario como leídas"""
        try:
            Notificacion.query.filter_by(
                usuario_id=usuario_id,
                leida=False
            ).update({
                'leida': True,
                'fecha_lectura': datetime.now(LOCAL_TZ)
            })
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al marcar todas como leídas: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def archivar_notificacion(notificacion_id: int, usuario_id: int):
        """Archiva una notificación"""
        try:
            notificacion = Notificacion.query.filter_by(
                id=notificacion_id,
                usuario_id=usuario_id
            ).first()
            
            if not notificacion:
                return None, "Notificación no encontrada"
            
            notificacion.archivada = True
            db.session.commit()
            
            return notificacion, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al archivar notificación: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def eliminar_notificacion(notificacion_id: int, usuario_id: int):
        """Elimina una notificación"""
        try:
            notificacion = Notificacion.query.filter_by(
                id=notificacion_id,
                usuario_id=usuario_id
            ).first()
            
            if not notificacion:
                return None, "Notificación no encontrada"
            
            db.session.delete(notificacion)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar notificación: {str(e)}")
            return False, str(e)
    
    # Métodos helper para crear notificaciones específicas
    
    @staticmethod
    def notificar_alerta_deuda(empleado_id: int, proyecto_id: int, horas_debidas: float):
        """Crea notificación de alerta de deuda de horas"""
        from app.models import Empleado, Proyecto
        
        empleado = Empleado.query.get(empleado_id)
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not empleado or not empleado.usuario_id or not proyecto:
            return None
        
        return NotificacionService.crear_notificacion(
            usuario_id=empleado.usuario_id,
            tipo='alerta_deuda',
            titulo='Alerta: Deuda de horas',
            mensaje=f'Tienes {horas_debidas} horas pendientes en el proyecto {proyecto.nombre}',
            metadatos={
                'proyecto_id': proyecto_id,
                'empleado_id': empleado_id,
                'horas_debidas': horas_debidas
            },
            url_accion=f'/proyecto/{proyecto_id}/empleado'
        )
    
    @staticmethod
    def notificar_recordatorio_marcado(empleado_id: int, proyecto_id: int, tipo: str):
        """Crea notificación de recordatorio para marcar entrada/salida"""
        from app.models import Empleado, Proyecto
        
        empleado = Empleado.query.get(empleado_id)
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not empleado or not empleado.usuario_id or not proyecto:
            return None
        
        accion = "entrada" if tipo == "entrada" else "salida"
        emoji = "🌅" if tipo == "entrada" else "🌙"
        
        return NotificacionService.crear_notificacion(
            usuario_id=empleado.usuario_id,
            tipo='recordatorio_marcado',
            titulo=f'{emoji} Recordatorio: Marca tu {accion}',
            mensaje=f'No olvides marcar tu {accion} en el proyecto {proyecto.nombre}',
            metadatos={
                'proyecto_id': proyecto_id,
                'empleado_id': empleado_id,
                'tipo_marcado': tipo
            },
            url_accion=f'/proyecto/{proyecto_id}/empleado'
        )
    
    @staticmethod
    def notificar_exceso_horario(empleado_id: int, proyecto_id: int, horas_extras: float):
        """Crea notificación de alerta por exceso de horario"""
        from app.models import Empleado, Proyecto
        
        empleado = Empleado.query.get(empleado_id)
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not empleado or not empleado.usuario_id or not proyecto:
            return None
        
        return NotificacionService.crear_notificacion(
            usuario_id=empleado.usuario_id,
            tipo='alerta_exceso_horario',
            titulo='⚠️ Exceso de horario detectado',
            mensaje=f'Has superado tu horario laboral en {horas_extras:.2f} horas. ¿Sigues trabajando?',
            metadatos={
                'proyecto_id': proyecto_id,
                'empleado_id': empleado_id,
                'horas_extras': horas_extras
            },
            url_accion=f'/proyecto/{proyecto_id}/empleado'
        )
    
    @staticmethod
    def notificar_salida_automatica(usuario_id: int, proyecto_id: int, fecha, hora_cierre):
        """Crea notificación de salida marcada automáticamente"""
        from app.models import Proyecto
        
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto:
            return None
        
        return NotificacionService.crear_notificacion(
            usuario_id=usuario_id,
            tipo='salida_automatica',
            titulo='🕒 Salida marcada automáticamente',
            mensaje=f'Tu salida fue marcada automáticamente a las {hora_cierre.strftime("%H:%M")} en {proyecto.nombre} el {fecha.strftime("%d/%m/%Y")}',
            metadatos={
                'proyecto_id': proyecto_id,
                'fecha': fecha.isoformat(),
                'hora_cierre': hora_cierre.strftime('%H:%M:%S')
            },
            url_accion=f'/proyecto/{proyecto_id}/empleado'
        )
    
    @staticmethod
    def notificar_admin_confirmacion_horas_extras(admin_usuario_id: int, proyecto_id: int, empleado_id: int):
        """Notifica al admin que debe confirmar horas extras"""
        from app.models import Proyecto, Empleado
        
        proyecto = Proyecto.query.get(proyecto_id)
        empleado = Empleado.query.get(empleado_id)
        
        if not proyecto or not empleado:
            return None
        
        return NotificacionService.crear_notificacion(
            usuario_id=admin_usuario_id,
            tipo='confirmacion_horas_extras_pendiente',
            titulo='⏰ Confirmación de horas extras pendiente',
            mensaje=f'{empleado.nombre} trabajó fuera de horario en {proyecto.nombre}. Confirma si las horas extras son válidas.',
            metadatos={
                'proyecto_id': proyecto_id,
                'empleado_id': empleado_id
            },
            url_accion=f'/proyecto/{proyecto_id}'
        )
