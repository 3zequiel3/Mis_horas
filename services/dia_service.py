from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Dia, Tarea, Usuario
from utils.formatters import formato_a_horas, horas_a_formato

def obtener_dias_mes(db: Session, proyecto_id: int, año: int, mes: int):
    """Obtiene todos los días de un mes específico del proyecto"""
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

def actualizar_horas_dia(db: Session, dia_id: int, horas_str: str, user_id: int):
    """
    Actualiza las horas de un día según la configuración del usuario
    IMPORTANTE: El usuario SIEMPRE ingresa en "Horas Trabajadas", 
    pero el cálculo cambia según usar_horas_reales
    """
    dia = db.query(Dia).filter(Dia.id == dia_id).first()
    if not dia:
        return None
    
    # Obtener configuración del usuario
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    usar_horas_reales = usuario.usar_horas_reales if usuario else False
    
    # Convertir string formato HH:MM a float
    horas_float = formato_a_horas(horas_str)
    
    # SIEMPRE guardar en horas_trabajadas lo que ingresa el usuario
    dia.horas_trabajadas = horas_float
    
    # Calcular horas_reales automáticamente
    dia.horas_reales = horas_float / 2
    
    db.commit()
    db.refresh(dia)
    
    return dia

def obtener_dia_por_id(db: Session, dia_id: int):
    """Obtiene un día por su ID"""
    return db.query(Dia).filter(Dia.id == dia_id).first()

def recalcular_tareas_afectadas(db: Session, dia):
    """Recalcula horas de todas las tareas que usan un día modificado"""
    from services.tarea_service import calcular_horas_tarea
    
    tareas_afectadas = db.query(Tarea).filter(
        Tarea.dias.contains(dia)
    ).all()
    
    # Obtener usuario del proyecto para saber qué campo usar
    usuario_id = dia.proyecto.usuario_id
    
    for tarea in tareas_afectadas:
        tarea.horas = calcular_horas_tarea(tarea, usuario_id)
    
    db.commit()
    return tareas_afectadas