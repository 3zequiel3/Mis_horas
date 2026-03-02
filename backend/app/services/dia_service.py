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
        """Obtiene días del mes, opcionalmente filtrados por empleado
        
        NOTA IMPORTANTE: En proyectos colaborativos, los DÍAS son compartidos por todos.
        Solo las TAREAS son individuales de cada colaborador.
        """
        query = Dia.query.filter(
            Dia.proyecto_id == proyecto_id,
            func.extract('year', Dia.fecha) == anio,
            func.extract('month', Dia.fecha) == mes
        )
        
        if empleado_id is not None:
            query = query.filter(Dia.empleado_id == empleado_id)
        else:
            # Para proyectos personales y colaborativos, días sin empleado
            # En colaborativos, todos ven los mismos días
            query = query.filter(Dia.empleado_id.is_(None))
        
        return query.order_by(Dia.fecha.asc()).all()
    
    @staticmethod
    def obtener_dia_por_id(dia_id: int):
        """Obtiene un día por ID"""
        return Dia.query.filter(Dia.id == dia_id).first()
    
    @staticmethod
    def actualizar_horas_dia(dia_id: int, horas_str: str, user_id: int):
        """Actualiza horas del día
        
        Para proyectos colaborativos, usa tabla dias_colaboradores (horas por colaborador).
        Para otros proyectos, usa dias.horas_trabajadas directamente.
        """
        from app.models.dia_colaborador import DiaColaborador
        from app.models.proyecto_colaborador import ProyectoColaborador
        
        dia = Dia.query.filter(Dia.id == dia_id).first()
        if not dia:
            return None
        
        # Obtener proyecto
        proyecto = Proyecto.query.filter(Proyecto.id == dia.proyecto_id).first()
        if not proyecto:
            return None
        
        horas_float = formato_a_horas(horas_str)
        
        # PROYECTOS COLABORATIVOS: usar tabla dias_colaboradores
        if proyecto.tipo_proyecto == 'colaborativo':
            # Obtener configuración del colaborador
            colaborador = ProyectoColaborador.query.filter_by(
                proyecto_id=proyecto.id,
                usuario_id=user_id,
                estado='aceptado'
            ).first()
            
            if not colaborador:
                return None
            
            # Buscar o crear registro en dias_colaboradores
            dia_colaborador = DiaColaborador.query.filter_by(
                dia_id=dia_id,
                usuario_colaborador_id=user_id
            ).first()
            
            if not dia_colaborador:
                dia_colaborador = DiaColaborador(
                    dia_id=dia_id,
                    usuario_colaborador_id=user_id
                )
                db.session.add(dia_colaborador)
            
            # Actualizar según configuración del COLABORADOR (no del proyecto)
            if colaborador.horas_reales_activas:
                dia_colaborador.horas_trabajadas = horas_float
                dia_colaborador.horas_reales = horas_float / 2
            else:
                dia_colaborador.horas_trabajadas = horas_float
                dia_colaborador.horas_reales = 0
            
            db.session.commit()
            
        else:
            # PROYECTOS PERSONALES/EMPLEADOS: usar dias.horas_trabajadas
            usar_horas_reales = proyecto.horas_reales_activas if proyecto else False
            
            if usar_horas_reales:
                dia.horas_trabajadas = horas_float
                dia.horas_reales = horas_float / 2
            else:
                dia.horas_trabajadas = horas_float
                dia.horas_reales = 0
            
            db.session.commit()
            db.session.refresh(dia)
            
            # Recalcular tareas afectadas solo si el día tiene tareas asociadas
            DiaService.recalcular_tareas_afectadas_optimizado(dia, dia.proyecto_id)
        
        return dia
    
    @staticmethod
    def recalcular_tareas_afectadas_optimizado(dia: Dia, proyecto_id: int):
        """Recalcula tareas afectadas solo si el día tiene tareas asociadas (optimizado)"""
        # Verificar primero si el día tiene tareas asociadas (más eficiente)
        tareas_count = db.session.query(func.count(tarea_dia.c.tarea_id)).filter(
            tarea_dia.c.dia_id == dia.id
        ).scalar()
        
        if tareas_count == 0:
            # No hay tareas asociadas, no es necesario recalcular
            return
        
        # Solo si hay tareas, las recalculamos
        DiaService.recalcular_tareas_afectadas(dia, proyecto_id)
    
    @staticmethod
    def recalcular_tareas_afectadas(dia: Dia, proyecto_id: int):
        """Recalcula tareas afectadas según la configuración del proyecto"""
        tareas = Tarea.query.join(tarea_dia).filter(
            tarea_dia.c.dia_id == dia.id
        ).all()
        
        # Obtener configuración del proyecto
        proyecto = Proyecto.query.filter(Proyecto.id == proyecto_id).first()
        usar_horas_reales = proyecto.horas_reales_activas if proyecto else False
        
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
            
            # Obtener configuración del proyecto
            proyecto = Proyecto.query.filter(Proyecto.id == dia.proyecto_id).first()
            usar_horas_reales = proyecto.horas_reales_activas if proyecto else False
            
            if usar_horas_reales:
                # Si el proyecto tiene horas reales activas, calcular como la mitad
                dia.horas_reales = horas_trabajadas / 2
            else:
                # Si no, limpiar horas_reales
                dia.horas_reales = 0
            
            db.session.commit()
            db.session.refresh(dia)
            
            # Recalcular tareas afectadas solo si el día tiene tareas asociadas
            DiaService.recalcular_tareas_afectadas_optimizado(dia, dia.proyecto_id)
            
            return dia
            
        except ValueError as e:
            print(f"Error parseando horarios: {e}")
            return None
    
    @staticmethod
    def actualizar_turnos_dia(dia_id: int, turno_manana_entrada_str: str = None, 
                             turno_manana_salida_str: str = None,
                             turno_tarde_entrada_str: str = None, 
                             turno_tarde_salida_str: str = None,
                             user_id: int = None):
        """
        Actualiza horarios por turnos y calcula horas_trabajadas y extras automáticamente.
        
        Lógica de horas extras:
        - Entrada anticipada (antes del rango): cuenta como extra si se cumplen las horas del turno
        - Salida tardía (después del rango): cuenta como extra
        - Las horas extras se calculan sumando todo el tiempo trabajado fuera del horario laboral estándar
        """
        from datetime import datetime, timedelta
        
        dia = Dia.query.filter(Dia.id == dia_id).first()
        if not dia:
            return None
        
        try:
            total_horas = 0
            horas_extras_calculadas = 0
            
            # Obtener proyecto para rangos de turnos
            proyecto = Proyecto.query.filter(Proyecto.id == dia.proyecto_id).first()
            
            # Parsear y calcular turno mañana
            if turno_manana_entrada_str and turno_manana_salida_str:
                entrada_m = datetime.strptime(turno_manana_entrada_str, '%H:%M').time()
                salida_m = datetime.strptime(turno_manana_salida_str, '%H:%M').time()
                
                entrada_dt = datetime.combine(datetime.today(), entrada_m)
                salida_dt = datetime.combine(datetime.today(), salida_m)
                
                if salida_dt < entrada_dt:
                    salida_dt += timedelta(days=1)
                
                horas_manana = (salida_dt - entrada_dt).total_seconds() / 3600
                total_horas += horas_manana
                
                # Calcular extras del turno mañana si hay rango configurado
                # Solo cuenta como extra si trabajó MÁS horas que las configuradas
                if proyecto and proyecto.turno_manana_inicio and proyecto.turno_manana_fin:
                    rango_inicio = datetime.combine(datetime.today(), proyecto.turno_manana_inicio)
                    rango_fin = datetime.combine(datetime.today(), proyecto.turno_manana_fin)
                    
                    horas_configuradas = (rango_fin - rango_inicio).total_seconds() / 3600
                    
                    # Solo hay extras si trabajó más horas que las configuradas
                    if horas_manana > horas_configuradas:
                        horas_extras_calculadas += (horas_manana - horas_configuradas)
                
                dia.turno_manana_entrada = entrada_m
                dia.turno_manana_salida = salida_m
            else:
                dia.turno_manana_entrada = None
                dia.turno_manana_salida = None
            
            # Parsear y calcular turno tarde
            if turno_tarde_entrada_str and turno_tarde_salida_str:
                entrada_t = datetime.strptime(turno_tarde_entrada_str, '%H:%M').time()
                salida_t = datetime.strptime(turno_tarde_salida_str, '%H:%M').time()
                
                entrada_dt = datetime.combine(datetime.today(), entrada_t)
                salida_dt = datetime.combine(datetime.today(), salida_t)
                
                if salida_dt < entrada_dt:
                    salida_dt += timedelta(days=1)
                
                horas_tarde = (salida_dt - entrada_dt).total_seconds() / 3600
                total_horas += horas_tarde
                
                # Calcular extras del turno tarde si hay rango configurado
                # Solo cuenta como extra si trabajó MÁS horas que las configuradas
                if proyecto and proyecto.turno_tarde_inicio and proyecto.turno_tarde_fin:
                    rango_inicio = datetime.combine(datetime.today(), proyecto.turno_tarde_inicio)
                    rango_fin = datetime.combine(datetime.today(), proyecto.turno_tarde_fin)
                    
                    horas_configuradas = (rango_fin - rango_inicio).total_seconds() / 3600
                    
                    # Solo hay extras si trabajó más horas que las configuradas
                    if horas_tarde > horas_configuradas:
                        horas_extras_calculadas += (horas_tarde - horas_configuradas)
                
                dia.turno_tarde_entrada = entrada_t
                dia.turno_tarde_salida = salida_t
            else:
                dia.turno_tarde_entrada = None
                dia.turno_tarde_salida = None
            
            # Actualizar horas trabajadas
            dia.horas_trabajadas = total_horas
            
            # Obtener configuración del proyecto para horas reales
            usar_horas_reales = proyecto.horas_reales_activas if proyecto else False
            
            if usar_horas_reales:
                # Si el proyecto tiene horas reales activas, calcular como la mitad
                dia.horas_reales = total_horas / 2
            else:
                # Si no, limpiar horas_reales
                dia.horas_reales = 0
            
            # Guardar horas extras calculadas
            dia.horas_extras = round(horas_extras_calculadas, 2) if horas_extras_calculadas > 0 else 0
            
            db.session.commit()
            db.session.refresh(dia)
            
            # Recalcular tareas solo si el día tiene tareas asociadas (optimizado)
            if user_id:
                DiaService.recalcular_tareas_afectadas_optimizado(dia, dia.proyecto_id)
            
            return dia
            
        except ValueError as e:
            print(f"Error parseando turnos: {e}")
            return None
