from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Tarea, Dia, Usuario
from utils.formatters import horas_a_formato

def obtener_dias_disponibles(db: Session, proyecto_id: int, año: int, mes: int, tarea_excluir_id=None):
    """Obtiene días del mes que NO están asignados a otras tareas"""
    # Todos los días del mes
    todos_dias = (
        db.query(Dia)
        .filter(
            Dia.proyecto_id == proyecto_id,
            func.extract('year', Dia.fecha) == año,
            func.extract('month', Dia.fecha) == mes
        )
        .order_by(Dia.fecha.asc())
        .all()
    )
    
    # Días ya asignados a otras tareas (excluyendo la tarea actual si se está editando)
    query_tareas = db.query(Tarea).filter(Tarea.proyecto_id == proyecto_id)
    if tarea_excluir_id:
        query_tareas = query_tareas.filter(Tarea.id != tarea_excluir_id)
    
    tareas_otras = query_tareas.all()
    dias_ocupados = set()
    
    for tarea in tareas_otras:
        for dia in tarea.dias:
            dias_ocupados.add(dia.id)
    
    # Filtrar días disponibles
    dias_disponibles = [dia for dia in todos_dias if dia.id not in dias_ocupados]
    return dias_disponibles

def crear_tarea(db: Session, proyecto_id: int, titulo: str, detalle: str = "", 
                que_falta: str = "", dias_ids: list = None, usuario_id: int = None):
    """Crea una nueva tarea asociada a días específicos"""
    nueva_tarea = Tarea(
        titulo=titulo,
        detalle=detalle,
        que_falta=que_falta,
        proyecto_id=proyecto_id,
        horas=""
    )
    
    # Asociar días si se proporcionaron
    if dias_ids:
        dias = db.query(Dia).filter(Dia.id.in_(dias_ids)).all()
        nueva_tarea.dias = dias
    
    db.add(nueva_tarea)
    db.commit()
    
    # Calcular horas después de asociar días
    if dias_ids and usuario_id:
        nueva_tarea.horas = calcular_horas_tarea(nueva_tarea, usuario_id)
        db.commit()
    
    db.refresh(nueva_tarea)
    return nueva_tarea

def actualizar_tarea(db: Session, tarea_id: int, titulo: str = None, 
                     detalle: str = None, que_falta: str = None, 
                     dias_ids: list = None, usuario_id: int = None):
    """Actualiza una tarea existente"""
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    
    if not tarea:
        return None
    
    # Actualizar campos básicos
    if titulo is not None:
        tarea.titulo = titulo
    if detalle is not None:
        tarea.detalle = detalle
    if que_falta is not None:
        tarea.que_falta = que_falta
    
    # Actualizar días asociados si se proporcionaron
    if dias_ids is not None:
        dias = db.query(Dia).filter(Dia.id.in_(dias_ids)).all()
        tarea.dias = dias
        # Recalcular horas
        if usuario_id:
            tarea.horas = calcular_horas_tarea(tarea, usuario_id)
    
    db.commit()
    db.refresh(tarea)
    return tarea

def eliminar_tarea(db: Session, tarea_id: int):
    """Elimina una tarea"""
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    
    if tarea:
        db.delete(tarea)
        db.commit()
        return True
    return False

def obtener_tareas_proyecto(db: Session, proyecto_id: int):
    """Obtiene todas las tareas de un proyecto"""
    return db.query(Tarea).filter(Tarea.proyecto_id == proyecto_id).all()

def calcular_horas_tarea(tarea: Tarea, usuario_id: int) -> str:
    """
    Calcula las horas totales de una tarea según configuración del usuario
    - Si usar_horas_reales = True: suma horas_reales
    - Si usar_horas_reales = False: suma horas_trabajadas
    """
    if not tarea.dias:
        return "00:00"
    
    # Obtener sesión desde el primer día
    db = tarea.dias[0]._sa_instance_state.session
    if not db:
        # Si no hay sesión en el objeto, intentar obtenerla de otra forma
        return "00:00"
    
    # Obtener configuración del usuario
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    usar_horas_reales = usuario.usar_horas_reales if usuario else False
    
    # Sumar según configuración
    if usar_horas_reales:
        total_horas = sum(dia.horas_reales for dia in tarea.dias)
    else:
        total_horas = sum(dia.horas_trabajadas for dia in tarea.dias)
    
    return horas_a_formato(total_horas)

def obtener_horas_tarea_segun_usuario(tarea: Tarea, usuario_id: int, db: Session) -> str:
    """
    Obtiene las horas de una tarea según la configuración del usuario
    Esta función es útil cuando ya tenemos la tarea cargada
    """
    if not tarea.dias:
        return "00:00"
    
    # Obtener configuración del usuario
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    usar_horas_reales = usuario.usar_horas_reales if usuario else False
    
    # Sumar según configuración
    if usar_horas_reales:
        total_horas = sum(dia.horas_reales for dia in tarea.dias)
    else:
        total_horas = sum(dia.horas_trabajadas for dia in tarea.dias)
    
    return horas_a_formato(total_horas)

def obtener_tarea_por_id(db: Session, tarea_id: int):
    """Obtiene una tarea por su ID"""
    return db.query(Tarea).filter(Tarea.id == tarea_id).first()