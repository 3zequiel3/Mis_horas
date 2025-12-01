from app import db
from app.models.proyecto import Proyecto
from app.models.dia import Dia
from app.models.usuario import Usuario
from app.models.empleado import Empleado
from sqlalchemy import func
from datetime import date, timedelta
from app.utils.constants import DIAS_ES
from app.utils.formatters import horas_a_formato
import calendar
from datetime import datetime as dt

class ProyectoService:
    @staticmethod
    def crear_proyecto(nombre: str, descripcion: str, anio: int, mes: int, usuario_id: int, 
                      organization_id: int,  # FASE 1 MULTI-TENANT: Nuevo parámetro obligatorio
                      tipo_proyecto: str = 'personal', empleados: list = None, 
                      horas_reales_activas: bool = False, modo_horarios: str = None,
                      horario_inicio: str = None, horario_fin: str = None,
                      turno_manana_inicio: str = None, turno_manana_fin: str = None,
                      turno_tarde_inicio: str = None, turno_tarde_fin: str = None,
                      client_name: str = None, brand_color: str = None,  # FASE 4: Nuevos campos
                      modules_config: dict = None,  # FASE 4: Configuración de módulos
                      budget_type: str = 'none', budget_base_amount: float = None,  # FASE 4: Presupuesto
                      currency: str = 'USD'):  # FASE 4: Moneda
        """Crea un nuevo proyecto - FASE 1 MULTI-TENANT + FASE 4 UX"""
        from datetime import datetime
        
        # Convertir strings de tiempo a objetos time
        def parse_time(time_str):
            if time_str:
                try:
                    return datetime.strptime(time_str, '%H:%M').time()
                except:
                    return None
            return None
        
        # FASE 4: Configuración de módulos por defecto
        if modules_config is None:
            modules_config = {
                'budget': False,
                'time_tracking': True,
                'audit': False,
                'public_view': False
            }
        
        # FASE 1 MULTI-TENANT: Incluir organization_id
        # FASE 4: Incluir client_name, brand_color, modules_config, budget
        proyecto = Proyecto(
            nombre=nombre,
            descripcion=descripcion,
            anio=anio,
            mes=mes,
            usuario_id=usuario_id,
            organization_id=organization_id,
            activo=True,
            tipo_proyecto=tipo_proyecto,
            horas_reales_activas=horas_reales_activas,
            modo_horarios=modo_horarios,
            horario_inicio=parse_time(horario_inicio),
            horario_fin=parse_time(horario_fin),
            turno_manana_inicio=parse_time(turno_manana_inicio),
            turno_manana_fin=parse_time(turno_manana_fin),
            turno_tarde_inicio=parse_time(turno_tarde_inicio),
            turno_tarde_fin=parse_time(turno_tarde_fin),
            client_name=client_name,
            brand_color=brand_color,
            modules_config=modules_config,
            budget_type=budget_type,
            budget_base_amount=budget_base_amount,
            currency=currency
        )
        
        db.session.add(proyecto)
        db.session.commit()
        db.session.refresh(proyecto)
        
        # Si es proyecto con empleados, crear empleados
        if tipo_proyecto == 'empleados' and empleados:
            for nombre_empleado in empleados:
                empleado = Empleado(
                    nombre=nombre_empleado,
                    proyecto_id=proyecto.id,
                    activo=True
                )
                db.session.add(empleado)
            db.session.commit()
        
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
        
        if proyecto.tipo_proyecto == 'personal':
            # Proyecto personal: crear días sin empleado
            for day in range(1, month_range + 1):
                fecha = dt(proyecto.anio, proyecto.mes, day).date()
                weekday = fecha.weekday()
                
                dia = Dia(
                    fecha=fecha,
                    dia_semana=DIAS_ES[weekday],
                    horas_trabajadas=0,
                    horas_reales=0,
                    proyecto_id=proyecto.id,
                    empleado_id=None
                )
                db.session.add(dia)
        else:
            # Proyecto con empleados: crear días para cada empleado
            empleados = Empleado.query.filter_by(proyecto_id=proyecto.id).all()
            for empleado in empleados:
                for day in range(1, month_range + 1):
                    fecha = dt(proyecto.anio, proyecto.mes, day).date()
                    weekday = fecha.weekday()
                    
                    dia = Dia(
                        fecha=fecha,
                        dia_semana=DIAS_ES[weekday],
                        horas_trabajadas=0,
                        horas_reales=0,
                        proyecto_id=proyecto.id,
                        empleado_id=empleado.id
                    )
                    db.session.add(dia)
        
        db.session.commit()
    
    @staticmethod
    def obtener_proyectos_usuario(usuario_id: int, organization_id: int):
        """Obtiene proyectos del usuario en una organización específica - FASE 1 MULTI-TENANT"""
        from app.models.empleado import Empleado
        
        # FASE 1 MULTI-TENANT: Filtrar por organization_id
        # Proyectos donde el usuario es el admin
        proyectos_admin = Proyecto.query.filter(
            Proyecto.usuario_id == usuario_id,
            Proyecto.organization_id == organization_id
        ).all()
        
        # Proyectos donde el usuario es empleado
        proyectos_empleado = Proyecto.query.join(
            Empleado, Empleado.proyecto_id == Proyecto.id
        ).filter(
            Empleado.usuario_id == usuario_id,
            Proyecto.organization_id == organization_id
        ).all()
        
        # Combinar y eliminar duplicados
        proyectos_ids = set()
        proyectos_unicos = []
        
        for proyecto in proyectos_admin + proyectos_empleado:
            if proyecto.id not in proyectos_ids:
                proyectos_ids.add(proyecto.id)
                proyectos_unicos.append(proyecto)
        
        # Ordenar: activos primero, luego por ID descendente
        return sorted(proyectos_unicos, key=lambda p: (not p.activo, -p.id))
    
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
            print(f"[AGREGAR_MES] Proyecto {proyecto_id} no encontrado")
            return False
        
        # Verificar si ya existe
        existing = Dia.query.filter(
            Dia.proyecto_id == proyecto_id,
            func.extract('year', Dia.fecha) == anio,
            func.extract('month', Dia.fecha) == mes
        ).first()
        
        if existing:
            print(f"[AGREGAR_MES] El mes {mes}/{anio} ya existe para proyecto {proyecto_id}")
            return False
        
        print(f"[AGREGAR_MES] Creando {calendar.monthrange(anio, mes)[1]} días para mes {mes}/{anio}")
        
        # Crear días
        month_range = calendar.monthrange(anio, mes)[1]
        
        if proyecto.tipo_proyecto == 'personal':
            # Proyecto personal
            for day in range(1, month_range + 1):
                fecha = dt(anio, mes, day).date()
                weekday = fecha.weekday()
                
                dia = Dia(
                    fecha=fecha,
                    dia_semana=DIAS_ES[weekday],
                    horas_trabajadas=0,
                    horas_reales=0,
                    proyecto_id=proyecto_id,
                    empleado_id=None
                )
                db.session.add(dia)
            print(f"[AGREGAR_MES] {month_range} días creados para proyecto personal")
        else:
            # Proyecto con empleados
            empleados = Empleado.query.filter_by(proyecto_id=proyecto_id).all()
            print(f"[AGREGAR_MES] Creando días para {len(empleados)} empleados")
            for empleado in empleados:
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
    def obtener_estadisticas_usuario(user_id: int, organization_id: int) -> dict:
        """
        Obtiene estadísticas del usuario en una organización específica - FASE 1 MULTI-TENANT
        Suma horas según la configuración de cada proyecto:
        - Si proyecto.horas_reales_activas: suma horas_reales
        - Si no: suma horas_trabajadas
        """
        # FASE 1 MULTI-TENANT: Filtrar por organization_id
        # Proyectos activos
        proyectos_activos = Proyecto.query.filter(
            Proyecto.usuario_id == user_id,
            Proyecto.organization_id == organization_id,
            Proyecto.activo == True
        ).count()
        
        # Obtener todos los proyectos del usuario en la organización
        proyectos = Proyecto.query.filter(
            Proyecto.usuario_id == user_id,
            Proyecto.organization_id == organization_id
        ).all()
        
        total_horas = 0
        horas_semana = 0
        total_dias = 0
        
        inicio_semana = date.today() - timedelta(days=7)
        
        # Calcular horas según la configuración de cada proyecto
        for proyecto in proyectos:
            usar_horas_reales = proyecto.horas_reales_activas
            campo_horas = Dia.horas_reales if usar_horas_reales else Dia.horas_trabajadas
            
            # Total horas del proyecto
            horas_proyecto = db.session.query(func.sum(campo_horas)).filter(
                Dia.proyecto_id == proyecto.id
            ).scalar() or 0
            total_horas += horas_proyecto
            
            # Horas semana del proyecto
            horas_semana_proyecto = db.session.query(func.sum(campo_horas)).filter(
                Dia.proyecto_id == proyecto.id,
                Dia.fecha >= inicio_semana
            ).scalar() or 0
            horas_semana += horas_semana_proyecto
            
            # Días con horas del proyecto
            dias_proyecto = db.session.query(func.count(Dia.id)).filter(
                Dia.proyecto_id == proyecto.id,
                campo_horas > 0
            ).scalar() or 0
            total_dias += dias_proyecto
        
        promedio_diario = total_horas / total_dias if total_dias > 0 else 0
        
        return {
            'proyectos_activos': proyectos_activos,
            'total_horas': total_horas,
            'horas_semana': horas_semana,
            'promedio_diario': promedio_diario
        }
    
    @staticmethod
    def eliminar_proyecto(proyecto_id: int):
        """Elimina un proyecto y todos sus datos asociados (días, tareas, empleados)"""
        proyecto = Proyecto.query.filter(Proyecto.id == proyecto_id).first()
        if not proyecto:
            return False
        
        # SQLAlchemy automáticamente eliminará:
        # - Días (cascade="all, delete-orphan")
        # - Tareas (cascade="all, delete-orphan")
        # - Empleados (cascade="all, delete-orphan")
        # - Relaciones en tarea_dia (por la configuración de la tabla intermedia)
        db.session.delete(proyecto)
        db.session.commit()
        return True
