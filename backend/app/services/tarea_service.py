from app import db
from app.models.tarea import Tarea
from app.models.dia import Dia, tarea_dia
from app.models.usuario import Usuario
from sqlalchemy import func, case
from app.utils.formatters import horas_a_formato

class TareaService:
    @staticmethod
    def _filtro_grupo_tareas(query, proyecto_id: int, mes: int, anio: int, usuario_colaborador_id: int = None):
        """Aplica filtro por grupo lógico de tareas."""
        query = query.filter(
            Tarea.proyecto_id == proyecto_id,
            Tarea.mes == mes,
            Tarea.anio == anio
        )

        if usuario_colaborador_id is None:
            query = query.filter(Tarea.usuario_colaborador_id.is_(None))
        else:
            query = query.filter(Tarea.usuario_colaborador_id == usuario_colaborador_id)

        return query

    @staticmethod
    def _obtener_siguiente_position(proyecto_id: int, mes: int, anio: int, usuario_colaborador_id: int = None) -> int:
        """Obtiene la siguiente posición disponible dentro del grupo lógico."""
        query = db.session.query(func.max(Tarea.position))
        query = TareaService._filtro_grupo_tareas(query, proyecto_id, mes, anio, usuario_colaborador_id)
        max_position = query.scalar()
        return (max_position or 0) + 1

    @staticmethod
    def crear_tarea(proyecto_id: int, titulo: str, mes: int, anio: int, detalle: str = "", 
                   que_falta: str = "", dias_ids: list = None, usuario_id: int = None,
                   usuario_colaborador_id: int = None, position: int = None):
        """Crea una nueva tarea"""
        from app.models.proyecto import Proyecto

        if position is None:
            # Compatibilidad legacy: nuevas tareas quedan sin orden manual explícito.
            position_final = 0
        else:
            position_final = max(1, int(position))
            tareas_a_mover = db.session.query(Tarea)
            tareas_a_mover = TareaService._filtro_grupo_tareas(
                tareas_a_mover,
                proyecto_id,
                mes,
                anio,
                usuario_colaborador_id
            ).filter(Tarea.position >= position_final)
            tareas_a_mover.update(
                {Tarea.position: Tarea.position + 1},
                synchronize_session=False
            )
        
        tarea = Tarea(
            titulo=titulo,
            detalle=detalle,
            que_falta=que_falta,
            proyecto_id=proyecto_id,
            mes=mes,
            anio=anio,
            horas="00:00",  # Inicializar con 00:00
            usuario_colaborador_id=usuario_colaborador_id,
            position=position_final
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
    def obtener_tareas_proyecto(proyecto_id: int, mes: int = None, anio: int = None, usuario_colaborador_id: int = None, es_propietario: bool = False):
        """Obtiene tareas del proyecto, opcionalmente filtradas por mes, año y colaborador"""
        from sqlalchemy import or_
        
        query = Tarea.query.filter(Tarea.proyecto_id == proyecto_id)
        
        if mes is not None:
            query = query.filter(Tarea.mes == mes)
        if anio is not None:
            query = query.filter(Tarea.anio == anio)
        
        # Filtrar por colaborador si se especifica
        if usuario_colaborador_id is not None:
            # Para proyectos colaborativos:
            # - Propietario: ve tareas con su ID O NULL (tareas previas a conversión)
            # - Colaborador: ve solo tareas con su ID
            if es_propietario:
                query = query.filter(
                    or_(
                        Tarea.usuario_colaborador_id == usuario_colaborador_id,
                        Tarea.usuario_colaborador_id.is_(None)
                    )
                )
            else:
                query = query.filter(Tarea.usuario_colaborador_id == usuario_colaborador_id)
        
        # Si position <= 0, cae a orden histórico por id (legacy sin orden manual).
        return query.order_by(
            case((Tarea.position > 0, 0), else_=1),
            Tarea.position.asc(),
            Tarea.id.asc()
        ).all()

    @staticmethod
    def reordenar_tareas(items: list):
        """Reordena tareas en batch dentro del mismo grupo lógico y normaliza a 1..N."""
        if not items:
            raise ValueError('Debes enviar al menos una tarea para reordenar')

        ids = [item.get('id') for item in items if isinstance(item, dict)]
        if len(ids) != len(items) or any(tarea_id is None for tarea_id in ids):
            raise ValueError('Cada item debe incluir id y position')

        if len(set(ids)) != len(ids):
            raise ValueError('No se permiten IDs duplicados en el payload')

        tareas_payload = Tarea.query.filter(Tarea.id.in_(ids)).all()
        if len(tareas_payload) != len(ids):
            raise LookupError('Una o más tareas no existen')

        primera = tareas_payload[0]
        grupo = {
            'proyecto_id': primera.proyecto_id,
            'mes': primera.mes,
            'anio': primera.anio,
            'usuario_colaborador_id': primera.usuario_colaborador_id
        }

        for tarea in tareas_payload:
            if (
                tarea.proyecto_id != grupo['proyecto_id'] or
                tarea.mes != grupo['mes'] or
                tarea.anio != grupo['anio'] or
                tarea.usuario_colaborador_id != grupo['usuario_colaborador_id']
            ):
                raise ValueError('Todas las tareas deben pertenecer al mismo grupo lógico')

        query_grupo = Tarea.query
        query_grupo = TareaService._filtro_grupo_tareas(
            query_grupo,
            grupo['proyecto_id'],
            grupo['mes'],
            grupo['anio'],
            grupo['usuario_colaborador_id']
        )
        tareas_grupo = query_grupo.all()

        if len(tareas_grupo) != len(ids):
            raise ValueError('Debes enviar todas las tareas del grupo para reordenar de forma consistente')

        tareas_por_id = {t.id: t for t in tareas_grupo}
        posiciones_payload = {}
        for item in items:
            try:
                pos = int(item.get('position'))
            except (TypeError, ValueError):
                raise ValueError('Cada item debe incluir position numérica')
            if pos < 1:
                raise ValueError('Las posiciones deben ser mayores o iguales a 1')
            posiciones_payload[int(item['id'])] = pos

        ids_ordenados = sorted(
            posiciones_payload.keys(),
            key=lambda tarea_id: (posiciones_payload[tarea_id], tarea_id)
        )

        for idx, tarea_id in enumerate(ids_ordenados, start=1):
            tareas_por_id[tarea_id].position = idx

        db.session.commit()

        return sorted(tareas_grupo, key=lambda tarea: (tarea.position, tarea.id))
    
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
        from app.models.proyecto_colaborador import ProyectoColaborador
        from app.models.dia_colaborador import DiaColaborador
        
        proyecto = Proyecto.query.filter(Proyecto.id == tarea.proyecto_id).first()
        
        # Para proyectos colaborativos, obtener horas desde dias_colaboradores
        if proyecto and proyecto.tipo_proyecto == 'colaborativo':
            # Obtener configuración del colaborador
            colaborador = ProyectoColaborador.query.filter_by(
                proyecto_id=tarea.proyecto_id,
                usuario_id=usuario_id,
                estado='aceptado'
            ).first()
            
            usar_horas_reales = colaborador.horas_reales_activas if colaborador else False
            total_horas = 0
            
            # Obtener horas desde dias_colaboradores
            dias_ids = [dia.id for dia in tarea.dias]
            horas_colaborador = DiaColaborador.query.filter(
                DiaColaborador.dia_id.in_(dias_ids),
                DiaColaborador.usuario_colaborador_id == usuario_id
            ).all()
            
            # Crear mapa de horas
            horas_map = {hc.dia_id: hc for hc in horas_colaborador}
            
            # Calcular total
            for dia in tarea.dias:
                if dia.id in horas_map:
                    hc = horas_map[dia.id]
                    if usar_horas_reales:
                        total_horas += hc.horas_reales or 0
                    else:
                        total_horas += hc.horas_trabajadas or 0
                elif proyecto.usuario_id == usuario_id:
                    # Propietario sin registro en dias_colaboradores: usar dias.horas
                    if usar_horas_reales:
                        total_horas += dia.horas_reales or 0
                    else:
                        total_horas += dia.horas_trabajadas or 0
        else:
            # Proyectos personales/empleados: usar dias.horas directamente
            usar_horas_reales = proyecto.horas_reales_activas if proyecto else False
            
            if usar_horas_reales:
                total_horas = sum(dia.horas_reales or 0 for dia in tarea.dias)
            else:
                total_horas = sum(dia.horas_trabajadas or 0 for dia in tarea.dias)
        
        return horas_a_formato(total_horas)
    
    @staticmethod
    def obtener_dias_disponibles(proyecto_id: int, anio: int, mes: int, usuario_id: int, tarea_excluir_id=None):
        """Obtiene días disponibles que tengan horas trabajadas"""
        from app.models.proyecto import Proyecto
        from app.models.dia_colaborador import DiaColaborador
        
        proyecto = Proyecto.query.get(proyecto_id)
        
        # Para proyectos colaborativos, obtener días desde dias_colaboradores
        if proyecto and proyecto.tipo_proyecto == 'colaborativo':
            # Obtener días con horas en dias_colaboradores para el usuario
            subquery = db.session.query(
                Dia.fecha,
                func.min(Dia.id).label('dia_id')
            ).join(
                DiaColaborador, 
                DiaColaborador.dia_id == Dia.id
            ).filter(
                Dia.proyecto_id == proyecto_id,
                func.extract('year', Dia.fecha) == anio,
                func.extract('month', Dia.fecha) == mes,
                DiaColaborador.usuario_colaborador_id == usuario_id,
                DiaColaborador.horas_trabajadas > 0
            ).group_by(Dia.fecha).subquery()
            
            # Si es propietario sin registros en dias_colaboradores, también incluir sus días históricos
            if proyecto.usuario_id == usuario_id:
                subquery_owner = db.session.query(
                    Dia.fecha,
                    func.min(Dia.id).label('dia_id')
                ).outerjoin(
                    DiaColaborador,
                    db.and_(
                        DiaColaborador.dia_id == Dia.id,
                        DiaColaborador.usuario_colaborador_id == usuario_id
                    )
                ).filter(
                    Dia.proyecto_id == proyecto_id,
                    func.extract('year', Dia.fecha) == anio,
                    func.extract('month', Dia.fecha) == mes,
                    Dia.horas_trabajadas > 0,
                    DiaColaborador.id == None  # Solo días sin registro en dias_colaboradores
                ).group_by(Dia.fecha).subquery()
                
                # Unir ambas subconsultas
                todos_dias_ids = db.session.query(subquery.c.dia_id).union(
                    db.session.query(subquery_owner.c.dia_id)
                ).all()
                
                dias_ids = [id[0] for id in todos_dias_ids]
                todos_dias = Dia.query.filter(Dia.id.in_(dias_ids)).order_by(Dia.fecha.asc()).all()
            else:
                # Para colaboradores, solo días desde dias_colaboradores
                todos_dias = Dia.query.join(
                    subquery,
                    Dia.id == subquery.c.dia_id
                ).order_by(Dia.fecha.asc()).all()
        else:
            # Proyectos personales/empleados: usar dias.horas directamente
            subquery = db.session.query(
                Dia.fecha,
                func.min(Dia.id).label('dia_id')
            ).filter(
                Dia.proyecto_id == proyecto_id,
                func.extract('year', Dia.fecha) == anio,
                func.extract('month', Dia.fecha) == mes,
                Dia.horas_trabajadas > 0
            ).group_by(Dia.fecha).subquery()
            
            todos_dias = Dia.query.join(
                subquery,
                Dia.id == subquery.c.dia_id
            ).order_by(Dia.fecha.asc()).all()
        
        # Días ocupados por tareas del proyecto
        # CORRECCIÓN: En proyectos colaborativos, un día está ocupado solo si el USUARIO ACTUAL tiene tarea en él
        # Cada colaborador puede tener su propia tarea en el mismo día
        query_tareas = Tarea.query.filter(Tarea.proyecto_id == proyecto_id)
        
        # Para proyectos colaborativos Y personales, solo considerar las tareas del usuario actual
        if proyecto and proyecto.tipo_proyecto == 'colaborativo':
            # En colaborativos: solo tareas del usuario actual
            query_tareas = query_tareas.filter(Tarea.usuario_colaborador_id == usuario_id)
        else:
            # En personales/empleados: tareas del usuario o sin colaborador asignado
            query_tareas = query_tareas.filter(
                db.or_(
                    Tarea.usuario_colaborador_id == usuario_id,
                    Tarea.usuario_colaborador_id == None  # Tareas sin colaborador asignado
                )
            )
        
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
