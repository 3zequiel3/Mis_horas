# proyecto_service.py
import datetime
import calendar
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from models import Proyecto, Dia, Tarea
from utils.constants import DIAS_ES

def obtener_meses_proyecto(db: Session, proyecto_id: int):
    """Obtiene todos los meses únicos que tiene un proyecto"""
    fechas_unicas = db.query(Dia.fecha).filter(Dia.proyecto_id == proyecto_id).distinct().all()
    años_meses = set()
    
    for fecha_tupla in fechas_unicas:
        fecha = fecha_tupla[0]
        años_meses.add((fecha.year, fecha.month))
    
    meses = sorted(list(años_meses))
    return meses

def generar_dias_para_proyecto(db: Session, proyecto: Proyecto):
    """Genera días para el mes inicial del proyecto"""
    existing = (
        db.query(Dia)
        .filter(Dia.proyecto_id == proyecto.id)
        .first()
    )
    if existing:
        return

    # Generar días para el mes/año del proyecto
    month_range = calendar.monthrange(proyecto.anio, proyecto.mes)[1]
    
    for day in range(1, month_range + 1):
        fecha = datetime.date(proyecto.anio, proyecto.mes, day)
        weekday = fecha.weekday()
        dia = Dia(
            fecha=fecha,
            dia_semana=DIAS_ES[weekday],
            horas_trabajadas=0,
            horas_reales=0,
            proyecto_id=proyecto.id,
        )
        db.add(dia)
    
    db.commit()

def agregar_mes_proyecto(db: Session, proyecto: Proyecto, año: int, mes: int):
    """Agrega un nuevo mes al proyecto"""
    existing = (
        db.query(Dia)
        .filter(
            Dia.proyecto_id == proyecto.id,
            func.extract('year', Dia.fecha) == año,
            func.extract('month', Dia.fecha) == mes
        )
        .first()
    )
    
    if existing:
        return False  # Ya existe
    
    # Generar días para el nuevo mes
    month_range = calendar.monthrange(año, mes)[1]
    for day in range(1, month_range + 1):
        fecha = datetime.date(año, mes, day)
        weekday = fecha.weekday()
        dia = Dia(
            fecha=fecha,
            dia_semana=DIAS_ES[weekday],
            horas_trabajadas=0,
            horas_reales=0,
            proyecto_id=proyecto.id,
        )
        db.add(dia)
    db.commit()
    return True

def crear_proyecto(db: Session, nombre: str, descripcion: str, anio: int, mes: int):
    """Crea un nuevo proyecto"""
    nuevo = Proyecto(
        nombre=nombre,
        descripcion=descripcion,
        anio=anio,
        mes=mes,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    generar_dias_para_proyecto(db, nuevo)
    return nuevo