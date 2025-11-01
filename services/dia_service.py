# dia_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Dia, Tarea
from utils.formatters import formato_a_horas

def obtener_dias_mes(db: Session, proyecto_id: int, año: int, mes: int):
    """Obtiene días de un mes específico"""
    return (
        db.query(Dia)
        .filter(
            Dia.proyecto_id == proyecto_id,
            func.extract('year', Dia.fecha) == año,
            func.extract('month', Dia.fecha) == mes
        )
        .order_by(Dia.fecha.asc())
        .all()
    )

def actualizar_horas_dia(db: Session, dia_id: int, horas_str: str):
    """Actualiza las horas de un día específico"""
    dia = db.query(Dia).filter(Dia.id == dia_id).first()
    if dia:
        horas_trabajadas = formato_a_horas(horas_str)
        dia.horas_trabajadas = horas_trabajadas
        dia.horas_reales = horas_trabajadas / 2
        db.commit()
        return dia
    return None

def recalcular_tareas_afectadas(db: Session, dia):
    """Recalcula horas de tareas que usan un día específico"""
    from services.tarea_service import calcular_horas_tarea
    
    tareas_afectadas = db.query(Tarea).filter(
        Tarea.dias.contains(dia)
    ).all()
    
    for tarea in tareas_afectadas:
        tarea.horas = calcular_horas_tarea(tarea)
    
    db.commit()
    return tareas_afectadas