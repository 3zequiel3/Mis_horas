import datetime
from datetime import date, timedelta 
import calendar
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from models import Proyecto, Dia, Tarea, Usuario
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
    """Genera días del mes inicial del proyecto si no existen"""
    existing = (
        db.query(Dia)
        .filter(Dia.proyecto_id == proyecto.id)
        .first()
    )
    if existing:
        return

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
    """Agrega un nuevo mes al proyecto si no existe"""
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
        return False
    
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

def crear_proyecto(db: Session, nombre: str, descripcion: str, anio: int, mes: int, usuario_id: int):
    """Crea un nuevo proyecto para un usuario específico"""
    nuevo = Proyecto(
        nombre=nombre,
        descripcion=descripcion,
        anio=anio,
        mes=mes,
        usuario_id=usuario_id,
        activo=True
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    generar_dias_para_proyecto(db, nuevo)
    return nuevo

def obtener_proyectos_usuario(db: Session, usuario_id: int):
    """Obtiene todos los proyectos de un usuario específico"""
    return (
        db.query(Proyecto)
        .filter(Proyecto.usuario_id == usuario_id)
        .order_by(Proyecto.activo.desc(), Proyecto.id.desc())
        .all()
    )

def obtener_proyectos_activos(db: Session, usuario_id: int):
    """Obtiene solo los proyectos activos de un usuario"""
    return (
        db.query(Proyecto)
        .filter(Proyecto.usuario_id == usuario_id, Proyecto.activo == True)
        .count()
    )

def cambiar_estado_proyecto(db: Session, proyecto_id: int, activo: bool):
    """Cambia el estado de un proyecto"""
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if proyecto:
        proyecto.activo = activo
        db.commit()
        return True
    return False

def obtener_estadisticas_usuario(db: Session, user_id: int) -> dict:
    """Obtiene estadísticas del usuario teniendo en cuenta usar_horas_reales"""
    
    # Obtener configuración del usuario
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    usar_horas_reales = usuario.usar_horas_reales if usuario else False
    
    # Proyectos activos
    proyectos_activos = db.query(Proyecto).filter(
        Proyecto.usuario_id == user_id,
        Proyecto.activo == True
    ).count()
    
    # Decidir qué campo usar según configuración
    campo_horas = Dia.horas_reales if usar_horas_reales else Dia.horas_trabajadas
    
    # Horas totales
    total_horas = db.query(func.sum(campo_horas)).join(
        Proyecto, Dia.proyecto_id == Proyecto.id
    ).filter(
        Proyecto.usuario_id == user_id
    ).scalar() or 0
    
    # Horas de esta semana (últimos 7 días)
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=7)
    
    horas_semana = db.query(func.sum(campo_horas)).join(
        Proyecto, Dia.proyecto_id == Proyecto.id
    ).filter(
        Proyecto.usuario_id == user_id,
        Dia.fecha >= inicio_semana
    ).scalar() or 0
    
    # Promedio diario (total de horas / días con registro)
    total_dias = db.query(func.count(Dia.id)).join(
        Proyecto, Dia.proyecto_id == Proyecto.id
    ).filter(
        Proyecto.usuario_id == user_id,
        campo_horas > 0
    ).scalar() or 0
    
    promedio_diario = total_horas / total_dias if total_dias > 0 else 0
    
    return {
        'proyectos_activos': proyectos_activos,
        'total_horas': total_horas,
        'horas_semana': horas_semana,
        'promedio_diario': promedio_diario,
        'usando_horas_reales': usar_horas_reales
    }