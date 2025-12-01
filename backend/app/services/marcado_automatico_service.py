"""
Servicio para marcado automático de salida
Este servicio debe ejecutarse periódicamente (cada 1 hora o al final del día)
"""

from app import db
from app.models import (
    MarcadoAsistencia, Empleado, Proyecto, 
    ConfiguracionAsistencia, Dia
)
from app.utils import (
    obtener_hora_cierre_turno,
    calcular_horas_extras
)
from datetime import datetime, date, time, timedelta, timezone
from app.services.notificacion_service import NotificacionService

LOCAL_TZ = timezone(timedelta(hours=-3))


class MarcadoAutomaticoService:
    """Servicio para procesar marcados automáticos de salida"""
    
    @staticmethod
    def procesar_marcados_automaticos():
        """
        Procesa todos los marcados sin salida que deberían tener salida automática
        Este método debe ejecutarse periódicamente (ej: cada hora o al final del día)
        """
        try:
            print(f"🕒 Iniciando proceso de marcado automático de salida - {datetime.now(LOCAL_TZ)}")
            
            # Obtener todos los proyectos con marcado automático activado
            proyectos = db.session.query(Proyecto).join(
                ConfiguracionAsistencia,
                Proyecto.id == ConfiguracionAsistencia.proyecto_id
            ).filter(
                ConfiguracionAsistencia.modo_asistencia_activo == True,
                ConfiguracionAsistencia.marcar_salida_automatica == True
            ).all()
            
            marcados_procesados = 0
            
            for proyecto in proyectos:
                config = ConfiguracionAsistencia.query.filter_by(
                    proyecto_id=proyecto.id
                ).first()
                
                if not config:
                    continue
                
                # Buscar marcados sin salida
                marcados_pendientes = MarcadoAsistencia.query.filter_by(
                    proyecto_id=proyecto.id,
                    salida_marcada_manualmente=False,
                    salida_marcada_automaticamente=False
                ).filter(
                    MarcadoAsistencia.hora_entrada.isnot(None),
                    MarcadoAsistencia.hora_salida.is_(None)
                ).all()
                
                for marcado in marcados_pendientes:
                    if MarcadoAutomaticoService._debe_marcar_salida_automatica(
                        marcado, proyecto, config
                    ):
                        MarcadoAutomaticoService._marcar_salida_automatica(
                            marcado, proyecto, config
                        )
                        marcados_procesados += 1
            
            db.session.commit()
            print(f"✅ Proceso completado. {marcados_procesados} marcados procesados automáticamente")
            
            return marcados_procesados
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en proceso de marcado automático: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
    @staticmethod
    def _debe_marcar_salida_automatica(marcado, proyecto, config):
        """
        Determina si un marcado debe tener salida automática
        
        Reglas:
        - Si ya pasó la hora de cierre del turno
        - Si es de un día anterior al actual
        - Si el empleado NO confirmó que sigue trabajando
        """
        ahora = datetime.now(LOCAL_TZ)
        fecha_actual = ahora.date()

        # Si el marcado es de días anteriores, definitivamente debe cerrarse
        if marcado.fecha < fecha_actual:
            return True

        # Si es de hoy, verificar si pasó la hora de cierre
        if marcado.fecha == fecha_actual:
            hora_cierre = obtener_hora_cierre_turno(proyecto, marcado.turno)

            if not hora_cierre:
                # Si no hay hora de cierre definida, no marcar automáticamente
                return False

            # Construir datetime aware para la hora de cierre en la fecha del marcado
            cierre_dt = datetime.combine(marcado.fecha, hora_cierre).replace(tzinfo=LOCAL_TZ)

            # Verificar si ya pasó la hora de cierre comparando datetimes
            if ahora >= cierre_dt:
                # Si el empleado confirmó que sigue trabajando, no marcar automáticamente
                if marcado.confirmacion_continua:
                    return False
                return True

        return False
    

    
    @staticmethod
    def _marcar_salida_automatica(marcado, proyecto, config):
        """Marca la salida automática en la hora de cierre del turno"""
        try:
            # Obtener hora de cierre
            hora_cierre = obtener_hora_cierre_turno(proyecto, marcado.turno)
            
            if not hora_cierre:
                print(f"⚠️ No se pudo determinar hora de cierre para marcado {marcado.id}")
                return
            
            # Marcar salida
            marcado.hora_salida = hora_cierre
            marcado.salida_marcada_automaticamente = True
            
            # Calcular horas trabajadas
            horas_trabajadas = marcado.calcular_horas_trabajadas()
            marcado.horas_trabajadas = horas_trabajadas
            
            # Calcular horas extras y normales
            horas_normales, horas_extras = calcular_horas_extras(
                horas_trabajadas, proyecto, marcado.turno
            )
            marcado.horas_normales = horas_normales
            marcado.horas_extras = horas_extras
            
            # Actualizar o crear registro en la tabla dias
            dia = Dia.query.filter_by(
                proyecto_id=proyecto.id,
                empleado_id=marcado.empleado_id,
                fecha=marcado.fecha
            ).first()
            
            if not dia:
                dia = Dia(
                    proyecto_id=proyecto.id,
                    empleado_id=marcado.empleado_id,
                    fecha=marcado.fecha,
                    dia_semana=marcado.fecha.strftime('%A')
                )
                db.session.add(dia)
            
            dia.horas_trabajadas = float(horas_trabajadas)
            dia.horas_reales = float(horas_trabajadas)
            dia.hora_entrada = marcado.hora_entrada
            dia.hora_salida = marcado.hora_salida
            dia.horas_extras = float(marcado.horas_extras)
            
            # Hacer flush para obtener el ID del dia antes de asignarlo
            db.session.flush()
            marcado.dia_id = dia.id
            
            # Agregar observación
            marcado.observaciones = (marcado.observaciones or '') + \
                f"\n[Salida marcada automáticamente el {datetime.now(LOCAL_TZ).strftime('%Y-%m-%d %H:%M:%S')}]"
            
            # Notificar al empleado
            empleado = Empleado.query.get(marcado.empleado_id)
            if empleado.usuario_id:
                NotificacionService.notificar_salida_automatica(
                    empleado.usuario_id,
                    proyecto.id,
                    marcado.fecha,
                    hora_cierre
                )
            
            print(f"✅ Salida automática marcada para empleado {marcado.empleado_id} " +
                  f"en proyecto {proyecto.nombre} - Hora: {hora_cierre}")
            # Commit por marcado para mantener la sesión consistente y aislar errores
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al marcar salida automática para marcado {getattr(marcado, 'id', 'N/A')}: {str(e)}")
            import traceback
            traceback.print_exc()
    

    
    @staticmethod
    def procesar_horas_extras_con_confirmacion():
        """
        Procesa las horas extras cuando el empleado confirmó que sigue trabajando
        y el admin debe aprobarlas
        """
        try:
            print(f"🕒 Procesando horas extras con confirmación de continuidad")
            
            # Buscar marcados con confirmación continua pero sin confirmación de admin
            marcados_pendientes = MarcadoAsistencia.query.filter_by(
                confirmacion_continua=True,
                confirmada_por_admin=False
            ).filter(
                MarcadoAsistencia.hora_salida.isnot(None)
            ).all()
            
            # Notificar al admin de cada proyecto
            proyectos_notificados = set()
            
            for marcado in marcados_pendientes:
                if marcado.proyecto_id not in proyectos_notificados:
                    proyecto = Proyecto.query.get(marcado.proyecto_id)
                    if proyecto:
                        NotificacionService.notificar_admin_confirmacion_horas_extras(
                            proyecto.usuario_id,
                            marcado.proyecto_id,
                            marcado.empleado_id
                        )
                        proyectos_notificados.add(marcado.proyecto_id)
            
            print(f"✅ Notificaciones enviadas a {len(proyectos_notificados)} admins")
            
        except Exception as e:
            print(f"❌ Error al procesar horas extras con confirmación: {str(e)}")


# Función standalone para ejecutar desde cron o scheduler
def ejecutar_marcado_automatico():
    """
    Función para ejecutar desde cron job o APScheduler
    Ejemplo cron: 0 * * * * (cada hora en punto)
    """
    from app import create_app, db
    
    app = create_app()
    with app.app_context():
        MarcadoAutomaticoService.procesar_marcados_automaticos()
        MarcadoAutomaticoService.procesar_horas_extras_con_confirmacion()


if __name__ == '__main__':
    ejecutar_marcado_automatico()
