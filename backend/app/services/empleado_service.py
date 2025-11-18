from app import db
from app.models.empleado import Empleado
from app.models.dia import Dia
from app.utils.constants import DIAS_ES
import calendar
from datetime import datetime as dt

class EmpleadoService:
    @staticmethod
    def obtener_empleados_proyecto(proyecto_id: int):
        """Obtiene todos los empleados de un proyecto"""
        return Empleado.query.filter_by(proyecto_id=proyecto_id).all()
    
    @staticmethod
    def obtener_empleado_por_id(empleado_id: int):
        """Obtiene un empleado por ID"""
        return Empleado.query.filter_by(id=empleado_id).first()
    
    @staticmethod
    def agregar_empleado(proyecto_id: int, nombre: str):
        """Agrega un empleado a un proyecto y genera sus días"""
        from app.models.proyecto import Proyecto
        
        proyecto = Proyecto.query.filter_by(id=proyecto_id).first()
        if not proyecto or proyecto.tipo_proyecto != 'empleados':
            return None
        
        # Crear empleado
        empleado = Empleado(
            nombre=nombre,
            proyecto_id=proyecto_id,
            activo=True
        )
        db.session.add(empleado)
        db.session.commit()
        db.session.refresh(empleado)
        
        # Generar días para todos los meses existentes del proyecto
        dias_existentes = db.session.query(
            db.func.extract('year', Dia.fecha).label('anio'),
            db.func.extract('month', Dia.fecha).label('mes')
        ).filter(Dia.proyecto_id == proyecto_id).distinct().all()
        
        for anio_mes in dias_existentes:
            anio = int(anio_mes[0])
            mes = int(anio_mes[1])
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
                    empleado_id=empleado.id
                )
                db.session.add(dia)
        
        db.session.commit()
        return empleado
    
    @staticmethod
    def actualizar_empleado(empleado_id: int, nombre: str = None, activo: bool = None):
        """Actualiza un empleado"""
        empleado = Empleado.query.filter_by(id=empleado_id).first()
        if not empleado:
            return False
        
        if nombre is not None:
            empleado.nombre = nombre
        if activo is not None:
            empleado.activo = activo
        
        db.session.commit()
        return True
    
    @staticmethod
    def eliminar_empleado(empleado_id: int):
        """Elimina un empleado y todos sus días"""
        empleado = Empleado.query.filter_by(id=empleado_id).first()
        if not empleado:
            return False
        
        # Los días se eliminarán automáticamente por el cascade
        db.session.delete(empleado)
        db.session.commit()
        return True
