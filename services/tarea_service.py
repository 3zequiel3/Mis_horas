from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Tarea, Dia
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

def calcular_horas_tarea(tarea):
    """Calcula las horas totales de una tarea sumando las horas reales de sus días"""
    total = sum(dia.horas_reales for dia in tarea.dias)
    return horas_a_formato(total)

def crear_tarea(db: Session, titulo: str, detalle: str, que_falta: str, proyecto_id: int, dias_seleccionados: list):
    """Crea una nueva tarea y le asigna los días seleccionados"""
    tarea = Tarea(
        titulo=titulo,
        detalle=detalle,
        horas="",
        que_falta=que_falta,
        proyecto_id=proyecto_id,
    )
    db.add(tarea)
    db.commit()
    db.refresh(tarea)

    # Asignar días seleccionados
    for dia in dias_seleccionados:
        tarea.dias.append(dia)
    
    # Calcular y guardar horas automáticamente
    tarea.horas = calcular_horas_tarea(tarea)
    db.commit()
    return tarea

def actualizar_tarea(db: Session, tarea_id: int, titulo: str, detalle: str, que_falta: str, dias_seleccionados: list):
    """Actualiza una tarea existente con nuevos datos y días"""
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        return None
    
    # Actualizar campos de texto
    tarea.titulo = titulo
    tarea.detalle = detalle
    tarea.que_falta = que_falta
    
    # Reemplazar días asignados
    tarea.dias.clear()
    for dia in dias_seleccionados:
        tarea.dias.append(dia)
    
    # Recalcular horas basado en nuevos días
    tarea.horas = calcular_horas_tarea(tarea)
    
    db.commit()
    return tarea

def obtener_tareas_proyecto(db: Session, proyecto_id: int):
    """Obtiene todas las tareas de un proyecto ordenadas por ID ascendente"""
    return (
        db.query(Tarea)
        .filter(Tarea.proyecto_id == proyecto_id)
        .order_by(Tarea.id.asc())
        .all()
    )

def eliminar_tarea(db: Session, tarea_id: int):
    """Elimina una tarea de la base de datos"""
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if tarea:
        db.delete(tarea)
        db.commit()
        return True
    return False