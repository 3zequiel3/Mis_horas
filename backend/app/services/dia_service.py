from app import db
from app.models.dia import Dia, tarea_dia
from app.models.tarea import Tarea
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto
from sqlalchemy import func
from app.utils.formatters import formato_a_horas, horas_a_formato

class DiaService:
    @staticmethod
    def obtener_dias_mes(proyecto_id: int, anio: int, mes: int, empleado_id: int = None):
        """Obtiene días del mes, opcionalmente filtrados por empleado"""
        query = Dia.query.filter(
            Dia.proyecto_id == proyecto_id,
            func.extract('year', Dia.fecha) == anio,
            func.extract('month', Dia.fecha) == mes
        )
        
        if empleado_id is not None:
            query = query.filter(Dia.empleado_id == empleado_id)
        else:
            # Para proyectos personales, solo días sin empleado
            query = query.filter(Dia.empleado_id.is_(None))
        
        return query.order_by(Dia.fecha.asc()).all()
    
    @staticmethod
    def obtener_dia_por_id(dia_id: int):
        """Obtiene un día por ID"""
        return Dia.query.filter(Dia.id == dia_id).first()
    
    @staticmethod
    def actualizar_horas_dia(dia_id: int, horas_str: str, user_id: int):
        """Actualiza horas del día"""
        dia = Dia.query.filter(Dia.id == dia_id).first()
        if not dia:
            return None
        
        usuario = Usuario.query.filter(Usuario.id == user_id).first()
        usar_horas_reales = usuario.usar_horas_reales if usuario else False
        
        horas_float = formato_a_horas(horas_str)
        
        # Actualizar según la configuración del usuario
        if usar_horas_reales:
            # Si usa horas reales:
            # - Guardar entrada en horas_trabajadas
            # - Calcular horas_reales como la mitad
            dia.horas_trabajadas = horas_float
            dia.horas_reales = horas_float / 2
        else:
            # Si NO usa horas reales:
            # - Guardar entrada en horas_trabajadas
            # - Limpiar horas_reales
            dia.horas_trabajadas = horas_float
            dia.horas_reales = 0
        
        db.session.commit()
        db.session.refresh(dia)
        
        # Recalcular tareas afectadas
        DiaService.recalcular_tareas_afectadas(dia, user_id)
        
        return dia
    
    @staticmethod
    def recalcular_tareas_afectadas(dia: Dia, user_id: int):
        """Recalcula tareas afectadas según la configuración del usuario"""
        tareas = Tarea.query.join(tarea_dia).filter(
            tarea_dia.c.dia_id == dia.id
        ).all()
        
        usuario = Usuario.query.filter(Usuario.id == user_id).first()
        usar_horas_reales = usuario.usar_horas_reales if usuario else False
        
        for tarea in tareas:
            if usar_horas_reales:
                # Si usa horas reales, suma horas_reales
                total_horas = sum(d.horas_reales for d in tarea.dias)
            else:
                # Si no usa horas reales, suma horas_trabajadas
                total_horas = sum(d.horas_trabajadas for d in tarea.dias)
            
            tarea.horas = horas_a_formato(total_horas)
        
        db.session.commit()
    
    @staticmethod
    def actualizar_horarios_dia(dia_id: int, hora_entrada_str: str, hora_salida_str: str, user_id: int):
        """Actualiza horarios de entrada/salida y calcula horas_trabajadas automáticamente"""
        from datetime import datetime, timedelta
        
        dia = Dia.query.filter(Dia.id == dia_id).first()
        if not dia:
            return None
        
        try:
            # Parsear horas (formato HH:MM)
            hora_entrada = datetime.strptime(hora_entrada_str, '%H:%M').time()
            hora_salida = datetime.strptime(hora_salida_str, '%H:%M').time()
            
            # Crear datetime para calcular diferencia
            entrada_dt = datetime.combine(datetime.today(), hora_entrada)
            salida_dt = datetime.combine(datetime.today(), hora_salida)
            
            # Si salida es menor que entrada, asumimos que pasó medianoche
            if salida_dt < entrada_dt:
                salida_dt += timedelta(days=1)
            
            # Calcular diferencia en horas
            diferencia = salida_dt - entrada_dt
            horas_trabajadas = diferencia.total_seconds() / 3600
            
            # Actualizar el día
            dia.hora_entrada = hora_entrada
            dia.hora_salida = hora_salida
            dia.horas_trabajadas = horas_trabajadas
            
            # Las horas_reales no se modifican en tablero de empleados
            # pero si existían, las mantenemos
            
            db.session.commit()
            db.session.refresh(dia)
            
            # Recalcular tareas afectadas
            DiaService.recalcular_tareas_afectadas(dia, user_id)
            
            return dia
            
        except ValueError as e:
            print(f"Error parseando horarios: {e}")
            return None
