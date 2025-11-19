from app import db
from app.models.tarea import Tarea
from app.models.dia import Dia, tarea_dia
from app.models.usuario import Usuario
from sqlalchemy import func
from app.utils.formatters import horas_a_formato

class TareaService:
    @staticmethod
    def crear_tarea(proyecto_id: int, titulo: str, detalle: str = "", 
                   que_falta: str = "", dias_ids: list = None, usuario_id: int = None):
        """Crea una nueva tarea"""
        from app.models.proyecto import Proyecto
        
        tarea = Tarea(
            titulo=titulo,
            detalle=detalle,
            que_falta=que_falta,
            proyecto_id=proyecto_id,
            horas="00:00"  # Inicializar con 00:00
        )
        
        if dias_ids:
            # Para proyectos de empleados, incluir todos los días con esas fechas
            proyecto = Proyecto.query.get(proyecto_id)
            if proyecto and proyecto.tipo_proyecto == 'empleados':
                # Obtener las fechas de los días seleccionados
                dias_seleccionados = Dia.query.filter(Dia.id.in_(dias_ids)).all()
                fechas = [dia.fecha for dia in dias_seleccionados]
                
                # Buscar TODOS los días con esas fechas (todos los empleados)
                dias = Dia.query.filter(
                    Dia.proyecto_id == proyecto_id,
                    Dia.fecha.in_(fechas)
                ).all()
            else:
                # Para proyectos personales, usar solo los IDs recibidos
                dias = Dia.query.filter(Dia.id.in_(dias_ids)).all()
            
            tarea.dias = dias
        
        db.session.add(tarea)
        db.session.commit()
        
        # Siempre recalcular horas
        if usuario_id:
            tarea.horas = TareaService.calcular_horas_tarea(tarea, usuario_id)
        else:
            # Sin usuario_id, calcular sumando horas_trabajadas directamente
            if tarea.dias:
                total_horas = sum(dia.horas_trabajadas or 0 for dia in tarea.dias)
                tarea.horas = horas_a_formato(total_horas)
        
        db.session.commit()
        
        return tarea
    
    @staticmethod
    def obtener_tareas_proyecto(proyecto_id: int):
        """Obtiene tareas del proyecto"""
        return Tarea.query.filter(Tarea.proyecto_id == proyecto_id).all()
    
    @staticmethod
    def obtener_tarea_por_id(tarea_id: int):
        """Obtiene una tarea por ID"""
        return Tarea.query.filter(Tarea.id == tarea_id).first()
    
    @staticmethod
    def actualizar_tarea(tarea_id: int, titulo: str = None, 
                        detalle: str = None, que_falta: str = None, 
                        dias_ids: list = None, usuario_id: int = None):
        """Actualiza una tarea"""
        tarea = Tarea.query.filter(Tarea.id == tarea_id).first()
        
        if not tarea:
            return None
        
        if titulo is not None:
            tarea.titulo = titulo
        if detalle is not None:
            tarea.detalle = detalle
        if que_falta is not None:
            tarea.que_falta = que_falta
        
        # Actualizar días si se proporciona (incluso si es lista vacía)
        if dias_ids is not None:
            if len(dias_ids) > 0:
                # Para proyectos de empleados, incluir todos los días con esas fechas
                from app.models.proyecto import Proyecto
                proyecto = Proyecto.query.get(tarea.proyecto_id)
                
                if proyecto and proyecto.tipo_proyecto == 'empleados':
                    # Obtener las fechas de los días seleccionados
                    dias_seleccionados = Dia.query.filter(Dia.id.in_(dias_ids)).all()
                    fechas = [dia.fecha for dia in dias_seleccionados]
                    
                    # Buscar TODOS los días con esas fechas (todos los empleados)
                    dias = Dia.query.filter(
                        Dia.proyecto_id == tarea.proyecto_id,
                        Dia.fecha.in_(fechas)
                    ).all()
                else:
                    # Para proyectos personales, usar solo los IDs recibidos
                    dias = Dia.query.filter(Dia.id.in_(dias_ids)).all()
                
                tarea.dias = dias
            else:
                # Si lista vacía, eliminar todos los días
                tarea.dias = []
            
            # Recalcular horas siempre que se actualizan los días
            if usuario_id:
                tarea.horas = TareaService.calcular_horas_tarea(tarea, usuario_id)
        
        db.session.commit()
        return tarea
    
    @staticmethod
    def eliminar_tarea(tarea_id: int):
        """Elimina una tarea"""
        tarea = Tarea.query.filter(Tarea.id == tarea_id).first()
        
        if tarea:
            db.session.delete(tarea)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def calcular_horas_tarea(tarea: Tarea, usuario_id: int) -> str:
        """Calcula horas de la tarea según la configuración del usuario y tipo de proyecto"""
        if not tarea.dias:
            return "00:00"
        
        from app.models.proyecto import Proyecto
        
        proyecto = Proyecto.query.filter(Proyecto.id == tarea.proyecto_id).first()
        usuario = Usuario.query.filter(Usuario.id == usuario_id).first()
        
        # Para proyectos de empleados, siempre usar horas_trabajadas
        if proyecto and proyecto.tipo_proyecto == 'empleados':
            # Suma horas_trabajadas de todos los días de todos los empleados
            total_horas = sum(dia.horas_trabajadas or 0 for dia in tarea.dias)
        else:
            # Para proyectos personales, usar configuración del usuario
            usar_horas_reales = usuario.usar_horas_reales if usuario else False
            
            if usar_horas_reales:
                total_horas = sum(dia.horas_reales or 0 for dia in tarea.dias)
            else:
                total_horas = sum(dia.horas_trabajadas or 0 for dia in tarea.dias)
        
        return horas_a_formato(total_horas)
    
    @staticmethod
    def obtener_dias_disponibles(proyecto_id: int, anio: int, mes: int, tarea_excluir_id=None):
        """Obtiene días disponibles que tengan horas trabajadas"""
        # Obtener fechas únicas con horas trabajadas
        subquery = db.session.query(
            Dia.fecha,
            func.min(Dia.id).label('dia_id')
        ).filter(
            Dia.proyecto_id == proyecto_id,
            func.extract('year', Dia.fecha) == anio,
            func.extract('month', Dia.fecha) == mes,
            Dia.horas_trabajadas > 0
        ).group_by(Dia.fecha).subquery()
        
        # Obtener los días usando los IDs únicos
        todos_dias = Dia.query.join(
            subquery,
            Dia.id == subquery.c.dia_id
        ).order_by(Dia.fecha.asc()).all()
        
        # Días ocupados
        query_tareas = Tarea.query.filter(Tarea.proyecto_id == proyecto_id)
        if tarea_excluir_id:
            query_tareas = query_tareas.filter(Tarea.id != tarea_excluir_id)
        
        tareas = query_tareas.all()
        dias_ocupados = set()
        
        for tarea in tareas:
            for dia in tarea.dias:
                dias_ocupados.add(dia.id)
        
        # Filtrar disponibles
        dias_disponibles = [dia for dia in todos_dias if dia.id not in dias_ocupados]
        return dias_disponibles
