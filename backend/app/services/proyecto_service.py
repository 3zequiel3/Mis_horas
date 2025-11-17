from app import db
from app.models.proyecto import Proyecto
from app.models.dia import Dia
from app.models.usuario import Usuario
from sqlalchemy import func
from datetime import date, timedelta
from app.utils.constants import DIAS_ES
from app.utils.formatters import horas_a_formato
import calendar
from datetime import datetime as dt

class ProyectoService:
    @staticmethod
    def crear_proyecto(nombre: str, descripcion: str, anio: int, mes: int, usuario_id: int):
        """Crea un nuevo proyecto"""
        proyecto = Proyecto(
            nombre=nombre,
            descripcion=descripcion,
            anio=anio,
            mes=mes,
            usuario_id=usuario_id,
            activo=True
        )
        
        db.session.add(proyecto)
        db.session.commit()
        db.session.refresh(proyecto)
        
        # Generar días
        ProyectoService.generar_dias_proyecto(proyecto)
        
        return proyecto
    
    @staticmethod
    def generar_dias_proyecto(proyecto: Proyecto):
        """Genera días para el proyecto"""
        existing = Dia.query.filter(Dia.proyecto_id == proyecto.id).first()
        if existing:
            return
        
        month_range = calendar.monthrange(proyecto.anio, proyecto.mes)[1]
        
        for day in range(1, month_range + 1):
            fecha = dt(proyecto.anio, proyecto.mes, day).date()
            weekday = fecha.weekday()
            
            dia = Dia(
                fecha=fecha,
                dia_semana=DIAS_ES[weekday],
                horas_trabajadas=0,
                horas_reales=0,
                proyecto_id=proyecto.id,
            )
            db.session.add(dia)
        
        db.session.commit()
    
    @staticmethod
    def obtener_proyectos_usuario(usuario_id: int):
        """Obtiene proyectos del usuario"""
        return Proyecto.query.filter(
            Proyecto.usuario_id == usuario_id
        ).order_by(Proyecto.activo.desc(), Proyecto.id.desc()).all()
    
    @staticmethod
    def obtener_proyecto_por_id(proyecto_id: int):
        """Obtiene un proyecto por ID"""
        return Proyecto.query.filter(Proyecto.id == proyecto_id).first()
    
    @staticmethod
    def obtener_meses_proyecto(proyecto_id: int):
        """Obtiene meses del proyecto"""
        fechas = db.session.query(Dia.fecha).filter(
            Dia.proyecto_id == proyecto_id
        ).distinct().all()
        
        años_meses = set()
        for fecha_tupla in fechas:
            fecha = fecha_tupla[0]
            años_meses.add((fecha.year, fecha.month))
        
        return sorted(list(años_meses))
    
    @staticmethod
    def agregar_mes_proyecto(proyecto_id: int, anio: int, mes: int):
        """Agrega un mes al proyecto"""
        proyecto = Proyecto.query.filter(Proyecto.id == proyecto_id).first()
        if not proyecto:
            return False
        
        # Verificar si ya existe
        existing = Dia.query.filter(
            Dia.proyecto_id == proyecto_id,
            func.extract('year', Dia.fecha) == anio,
            func.extract('month', Dia.fecha) == mes
        ).first()
        
        if existing:
            return False
        
        # Crear días
        month_range = calendar.monthrange(anio, mes)[1]
        for day in range(1, month_range + 1):
            fecha = dt(anio, mes, day).date()
            weekday = fecha.weekday()
            
            dia = Dia(
                fecha=fecha,
                dia_semana=DIAS_ES[weekday],
                horas_trabajadas=0,
                horas_reales=0,
                proyecto_id=proyecto_id,
            )
            db.session.add(dia)
        
        db.session.commit()
        return True
    
    @staticmethod
    def cambiar_estado_proyecto(proyecto_id: int, activo: bool):
        """Cambia estado del proyecto"""
        proyecto = Proyecto.query.filter(Proyecto.id == proyecto_id).first()
        if proyecto:
            proyecto.activo = activo
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def obtener_estadisticas_usuario(user_id: int) -> dict:
        """Obtiene estadísticas del usuario"""
        usuario = Usuario.query.filter(Usuario.id == user_id).first()
        usar_horas_reales = usuario.usar_horas_reales if usuario else False
        
        # Proyectos activos
        proyectos_activos = Proyecto.query.filter(
            Proyecto.usuario_id == user_id,
            Proyecto.activo == True
        ).count()
        
        # Campo a usar
        campo_horas = Dia.horas_reales if usar_horas_reales else Dia.horas_trabajadas
        
        # Total horas
        total_horas = db.session.query(func.sum(campo_horas)).join(
            Proyecto, Dia.proyecto_id == Proyecto.id
        ).filter(Proyecto.usuario_id == user_id).scalar() or 0
        
        # Horas semana
        inicio_semana = date.today() - timedelta(days=7)
        horas_semana = db.session.query(func.sum(campo_horas)).join(
            Proyecto, Dia.proyecto_id == Proyecto.id
        ).filter(
            Proyecto.usuario_id == user_id,
            Dia.fecha >= inicio_semana
        ).scalar() or 0
        
        # Promedio diario
        total_dias = db.session.query(func.count(Dia.id)).join(
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
    
    @staticmethod
    def eliminar_proyecto(proyecto_id: int):
        """Elimina un proyecto y sus días asociados"""
        proyecto = Proyecto.query.filter(Proyecto.id == proyecto_id).first()
        if not proyecto:
            return False
        
        # Eliminar días del proyecto
        Dia.query.filter(Dia.proyecto_id == proyecto_id).delete()
        
        # Eliminar proyecto
        db.session.delete(proyecto)
        db.session.commit()
        return True
