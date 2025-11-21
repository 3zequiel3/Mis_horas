"""
Servicio para gestión de marcado de asistencia y cálculo de horas
"""

from app import db
from app.models import (
    MarcadoAsistencia, Empleado, Proyecto, Dia, 
    ConfiguracionAsistencia, DeudaHoras
)
from app.services.notificacion_service import NotificacionService
from app.utils import (
    calcular_horas_extras,
    obtener_configuracion_asistencia,
    calcular_horas_debidas_dia
)
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional, Tuple

LOCAL_TZ = timezone(timedelta(hours=-3))


class AsistenciaService:
    """Servicio para manejar el marcado de asistencia de empleados"""
    
    @staticmethod
    def marcar_entrada(empleado_id: int, proyecto_id: int, fecha: date = None, hora: time = None):
        """
        Marca la entrada de un empleado
        
        Args:
            empleado_id: ID del empleado
            proyecto_id: ID del proyecto
            fecha: Fecha del marcado (default: hoy)
            hora: Hora del marcado (default: ahora)
        
        Returns:
            Marcado creado o None si hay error
        """
        try:
            if fecha is None:
                fecha = datetime.now(LOCAL_TZ).date()
            if hora is None:
                hora = datetime.now(LOCAL_TZ).time()
            
            # Verificar que el empleado y proyecto existen
            empleado = Empleado.query.get(empleado_id)
            proyecto = Proyecto.query.get(proyecto_id)
            
            if not empleado or not proyecto:
                return None, "Empleado o proyecto no encontrado"
            
            # Verificar que no exista ya un marcado para este día
            marcado_existente = MarcadoAsistencia.query.filter_by(
                empleado_id=empleado_id,
                proyecto_id=proyecto_id,
                fecha=fecha
            ).first()
            
            if marcado_existente and marcado_existente.hora_entrada:
                return None, "Ya existe un marcado de entrada para este día"
            
            # Crear o actualizar marcado
            if marcado_existente:
                marcado = marcado_existente
            else:
                marcado = MarcadoAsistencia(
                    empleado_id=empleado_id,
                    proyecto_id=proyecto_id,
                    fecha=fecha
                )
            
            marcado.hora_entrada = hora
            marcado.entrada_marcada_manualmente = True
            
            # Detectar turno automáticamente
            marcado.turno = marcado.detectar_turno_automatico(proyecto)
            
            if not marcado_existente:
                db.session.add(marcado)
            
            db.session.commit()
            
            return marcado, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al marcar entrada: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def marcar_salida(
        empleado_id: int, 
        proyecto_id: int, 
        fecha: date = None, 
        hora: time = None,
        confirmar_continuidad: bool = False
    ):
        """
        Marca la salida de un empleado
        
        Args:
            empleado_id: ID del empleado
            proyecto_id: ID del proyecto
            fecha: Fecha del marcado (default: hoy)
            hora: Hora del marcado (default: ahora)
            confirmar_continuidad: Si el empleado confirmó que sigue trabajando
        
        Returns:
            Marcado actualizado o None si hay error
        """
        try:
            if fecha is None:
                fecha = datetime.now(LOCAL_TZ).date()
            if hora is None:
                hora = datetime.now(LOCAL_TZ).time()
            
            # Buscar el marcado de entrada
            marcado = MarcadoAsistencia.query.filter_by(
                empleado_id=empleado_id,
                proyecto_id=proyecto_id,
                fecha=fecha
            ).first()
            
            if not marcado or not marcado.hora_entrada:
                return None, "No se encontró un marcado de entrada para este día"
            
            if marcado.hora_salida:
                return None, "Ya existe un marcado de salida para este día"
            
            # Marcar salida
            marcado.hora_salida = hora
            marcado.salida_marcada_manualmente = True
            marcado.confirmacion_continua = confirmar_continuidad
            
            # Calcular horas trabajadas
            horas_trabajadas = marcado.calcular_horas_trabajadas()
            marcado.horas_trabajadas = horas_trabajadas
            
            # Calcular horas extras y normales
            proyecto = Proyecto.query.get(proyecto_id)
            config = obtener_configuracion_asistencia(proyecto_id)
            
            if config and config.modo_asistencia_activo:
                horas_normales, horas_extras = calcular_horas_extras(
                    horas_trabajadas, proyecto, marcado.turno
                )
                marcado.horas_normales = horas_normales
                marcado.horas_extras = horas_extras
            else:
                marcado.horas_normales = horas_trabajadas
                marcado.horas_extras = 0
            
            # Actualizar o crear registro en la tabla dias
            dia = Dia.query.filter_by(
                proyecto_id=proyecto_id,
                empleado_id=empleado_id,
                fecha=fecha
            ).first()
            
            if not dia:
                dia = Dia(
                    proyecto_id=proyecto_id,
                    empleado_id=empleado_id,
                    fecha=fecha,
                    dia_semana=fecha.strftime('%A')
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
            
            db.session.commit()
            
            # Procesar horas extras según política
            if marcado.horas_extras > 0 and config:
                AsistenciaService._procesar_horas_extras(
                    empleado_id, proyecto_id, marcado.horas_extras, config
                )
            
            return marcado, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al marcar salida: {str(e)}")
            return None, str(e)
    

    
    @staticmethod
    def _procesar_horas_extras(empleado_id: int, proyecto_id: int, horas_extras: float, config):
        """Procesa las horas extras según la política configurada"""
        politica = config.politica_horas_extras
        
        if politica == 'compensar_deuda':
            # Buscar deudas activas del empleado
            deudas = DeudaHoras.query.filter_by(
                empleado_id=empleado_id,
                proyecto_id=proyecto_id,
                estado='activa'
            ).order_by(DeudaHoras.fecha_inicio).all()
            
            horas_restantes = horas_extras
            
            for deuda in deudas:
                if horas_restantes <= 0:
                    break
                horas_restantes = deuda.compensar_con_horas_extras(horas_restantes)
            
        elif politica == 'bloquear_extras':
            # Las horas extras no se registran si hay deudas
            deudas_activas = DeudaHoras.query.filter_by(
                empleado_id=empleado_id,
                proyecto_id=proyecto_id,
                estado='activa'
            ).count()
            
            if deudas_activas > 0:
                # Las horas extras no cuentan
                pass
        
        # elif politica == 'separar_cuentas': No hace nada, se mantienen separadas
    
    @staticmethod
    def obtener_marcados_empleado(
        empleado_id: int, 
        proyecto_id: int, 
        fecha_inicio: date = None, 
        fecha_fin: date = None
    ):
        """Obtiene los marcados de un empleado en un rango de fechas"""
        query = MarcadoAsistencia.query.filter_by(
            empleado_id=empleado_id,
            proyecto_id=proyecto_id
        )
        
        if fecha_inicio:
            query = query.filter(MarcadoAsistencia.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.filter(MarcadoAsistencia.fecha <= fecha_fin)
        
        marcados = query.order_by(MarcadoAsistencia.fecha.desc()).all()
        
        return [m.to_dict() for m in marcados]
    
    @staticmethod
    def detectar_ausencias(proyecto_id: int, fecha: date):
        """
        Detecta empleados ausentes en una fecha y crea registros de deuda
        """
        try:
            config = ConfiguracionAsistencia.query.filter_by(proyecto_id=proyecto_id).first()
            
            if not config or not config.modo_asistencia_activo:
                return
            
            # Obtener empleados activos del proyecto
            empleados = Empleado.query.filter_by(
                proyecto_id=proyecto_id,
                activo=True,
                estado_asistencia='activo'
            ).all()
            
            proyecto = Proyecto.query.get(proyecto_id)
            
            for empleado in empleados:
                # Verificar si tiene marcado para ese día
                marcado = MarcadoAsistencia.query.filter_by(
                    empleado_id=empleado.id,
                    proyecto_id=proyecto_id,
                    fecha=fecha
                ).first()
                
                if not marcado or not marcado.hora_entrada:
                    # Empleado ausente, calcular horas debidas
                    horas_debidas = calcular_horas_debidas_dia(proyecto, empleado)
                    
                    if horas_debidas > 0:
                        # Crear o actualizar deuda
                        deuda = DeudaHoras(
                            empleado_id=empleado.id,
                            proyecto_id=proyecto_id,
                            fecha_inicio=fecha,
                            horas_debidas=horas_debidas,
                            motivo='ausencia',
                            descripcion_automatica=f'Ausencia detectada el {fecha.strftime("%d/%m/%Y")}'
                        )
                        db.session.add(deuda)
                        
                        # Notificar si está configurado
                        if config.enviar_alerta_deuda:
                            NotificacionService.notificar_alerta_deuda(
                                empleado.id, proyecto_id, horas_debidas
                            )
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al detectar ausencias: {str(e)}")

