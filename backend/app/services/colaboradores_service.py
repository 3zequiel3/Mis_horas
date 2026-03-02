"""
Servicio para gestión de colaboradores en proyectos colaborativos
"""

from app import db
from app.models.proyecto import Proyecto
from app.models.proyecto_colaborador import ProyectoColaborador
from app.models.usuario import Usuario
from app.models.dia import Dia
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, and_

# Zona horaria local
LOCAL_TZ = timezone(timedelta(hours=-3))


class ColaboradoresService:
    
    @staticmethod
    def convertir_a_colaborativo(proyecto_id: int, usuario_owner_id: int):
        """
        Convierte un proyecto personal a colaborativo
        y agrega al usuario actual como owner
        """
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto:
            return None, "Proyecto no encontrado"
        
        if proyecto.tipo_proyecto == 'empleados':
            return None, "No se puede convertir un proyecto de empleados a colaborativo"
        
        if proyecto.tipo_proyecto == 'colaborativo':
            return proyecto, None  # Ya es colaborativo
        
        # Cambiar tipo de proyecto
        proyecto.tipo_proyecto = 'colaborativo'
        
        # Agregar al usuario como owner si no existe
        colaborador_existente = ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            usuario_id=usuario_owner_id
        ).first()
        
        if not colaborador_existente:
            owner = ProyectoColaborador(
                proyecto_id=proyecto_id,
                usuario_id=usuario_owner_id,
                rol='owner',
                horas_reales_activas=proyecto.horas_reales_activas,
                estado='aceptado',
                fecha_aceptacion=datetime.now(LOCAL_TZ)
            )
            db.session.add(owner)
        
        db.session.commit()
        db.session.refresh(proyecto)
        
        return proyecto, None
    
    @staticmethod
    def invitar_colaborador(proyecto_id: int, email_usuario: str, horas_reales_activas: bool = False):
        """
        Invita a un usuario a ser colaborador de un proyecto
        """
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto:
            return None, "Proyecto no encontrado"
        
        if proyecto.tipo_proyecto != 'colaborativo':
            return None, "Solo los proyectos colaborativos pueden tener colaboradores"
        
        # Buscar usuario por email
        usuario = Usuario.query.filter_by(email=email_usuario).first()
        
        if not usuario:
            return None, f"No existe un usuario registrado con el email {email_usuario}"
        
        # Verificar si ya es colaborador
        colaborador_existente = ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            usuario_id=usuario.id
        ).first()
        
        if colaborador_existente:
            # Si tiene fecha_salida, significa que salió y puede ser reinvitado
            if colaborador_existente.fecha_salida:
                # Reactivar colaborador
                colaborador_existente.estado = 'aceptado'
                colaborador_existente.fecha_invitacion = datetime.now(LOCAL_TZ)
                colaborador_existente.fecha_aceptacion = datetime.now(LOCAL_TZ)
                colaborador_existente.fecha_salida = None
                colaborador_existente.horas_reales_activas = horas_reales_activas
                db.session.commit()
                return colaborador_existente, None
            
            if colaborador_existente.estado == 'aceptado':
                return None, "Este usuario ya es colaborador del proyecto"
            elif colaborador_existente.estado == 'pendiente':
                return None, "Este usuario ya tiene una invitación pendiente"
            elif colaborador_existente.estado == 'rechazado':
                # Reactivar invitación
                colaborador_existente.estado = 'aceptado'
                colaborador_existente.fecha_invitacion = datetime.now(LOCAL_TZ)
                colaborador_existente.fecha_aceptacion = datetime.now(LOCAL_TZ)
                colaborador_existente.horas_reales_activas = horas_reales_activas
                db.session.commit()
                return colaborador_existente, None
        
        # Crear nuevo colaborador
        colaborador = ProyectoColaborador(
            proyecto_id=proyecto_id,
            usuario_id=usuario.id,
            rol='colaborador',
            horas_reales_activas=horas_reales_activas,
            estado='aceptado',  # Auto-aceptado por ahora (se puede cambiar a 'pendiente' para flujo con notificaciones)
            fecha_invitacion=datetime.now(LOCAL_TZ),
            fecha_aceptacion=datetime.now(LOCAL_TZ)
        )
        
        db.session.add(colaborador)
        db.session.commit()
        db.session.refresh(colaborador)
        
        return colaborador, None
    
    @staticmethod
    def listar_colaboradores(proyecto_id: int, incluir_estadisticas: bool = False):
        """
        Lista todos los colaboradores de un proyecto
        """
        colaboradores = ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            estado='aceptado'
        ).all()
        
        return [c.to_dict(incluir_usuario=True, incluir_estadisticas=incluir_estadisticas) for c in colaboradores]
    
    @staticmethod
    def eliminar_colaborador(proyecto_id: int, usuario_id: int, usuario_solicitante_id: int):
        """
        Elimina un colaborador del proyecto
        Solo el owner puede eliminar colaboradores
        """
        # Verificar que el solicitante es owner
        es_owner = ProyectoColaborador.es_owner(proyecto_id, usuario_solicitante_id)
        
        if not es_owner:
            return False, "Solo el dueño del proyecto puede eliminar colaboradores"
        
        colaborador = ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            usuario_id=usuario_id
        ).first()
        
        if not colaborador:
            return False, "Colaborador no encontrado"
        
        if colaborador.rol == 'owner':
            return False, "No se puede eliminar al dueño del proyecto"
        
        # Marcar fecha de salida en lugar de eliminar (para historial)
        colaborador.fecha_salida = datetime.now(LOCAL_TZ)
        colaborador.estado = 'rechazado'
        
        db.session.commit()
        
        return True, None
    
    @staticmethod
    def actualizar_configuracion_colaborador(proyecto_id: int, usuario_id: int, horas_reales_activas: bool):
        """
        Actualiza la configuración de un colaborador
        """
        colaborador = ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            usuario_id=usuario_id,
            estado='aceptado'
        ).first()
        
        if not colaborador:
            return None, "Colaborador no encontrado"
        
        colaborador.horas_reales_activas = horas_reales_activas
        db.session.commit()
        db.session.refresh(colaborador)
        
        return colaborador, None
    
    @staticmethod
    def obtener_estadisticas_proyecto(proyecto_id: int):
        """
        Obtiene estadísticas generales del proyecto colaborativo
        Total de colaboradores, horas totales, etc.
        """
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto or proyecto.tipo_proyecto != 'colaborativo':
            return None
        
        # Contar colaboradores activos
        total_colaboradores = ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            estado='aceptado'
        ).count()
        
        # Calcular total de horas desde dias_colaboradores (horas individuales por colaborador)
        from app.models.dia_colaborador import DiaColaborador
        
        total_horas_trabajadas = db.session.query(
            func.sum(DiaColaborador.horas_trabajadas)
        ).join(
            Dia, DiaColaborador.dia_id == Dia.id
        ).filter(
            Dia.proyecto_id == proyecto_id
        ).scalar() or 0
        
        total_horas_reales = db.session.query(
            func.sum(DiaColaborador.horas_reales)
        ).join(
            Dia, DiaColaborador.dia_id == Dia.id
        ).filter(
            Dia.proyecto_id == proyecto_id
        ).scalar() or 0
        
        # Colaborador con más horas
        colaborador_mas_horas = db.session.query(
            DiaColaborador.usuario_colaborador_id,
            func.sum(DiaColaborador.horas_trabajadas).label('total')
        ).join(
            Dia, DiaColaborador.dia_id == Dia.id
        ).filter(
            Dia.proyecto_id == proyecto_id
        ).group_by(
            DiaColaborador.usuario_colaborador_id
        ).order_by(
            func.sum(DiaColaborador.horas_trabajadas).desc()
        ).first()
        
        top_colaborador = None
        if colaborador_mas_horas:
            usuario = Usuario.query.get(colaborador_mas_horas[0])
            if usuario:
                top_colaborador = {
                    'usuario_id': usuario.id,
                    'nombre': usuario.nombre_completo or usuario.username,
                    'total_horas': float(colaborador_mas_horas[1])
                }
        
        return {
            'total_colaboradores': total_colaboradores,
            'total_horas_trabajadas': float(total_horas_trabajadas),
            'total_horas_reales': float(total_horas_reales),
            'top_colaborador': top_colaborador,
        }
    
    @staticmethod
    def verificar_acceso_colaborador(proyecto_id: int, usuario_id: int):
        """
        Verifica si un usuario tiene acceso a un proyecto como colaborador
        Retorna: (tiene_acceso, es_owner, configuracion)
        """
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto:
            return False, False, None
        
        # Si no es colaborativo, verificar acceso tradicional
        if proyecto.tipo_proyecto != 'colaborativo':
            es_dueno = proyecto.usuario_id == usuario_id
            return es_dueno, es_dueno, None
        
        # Para proyectos colaborativos, verificar en tabla de colaboradores
        colaborador = ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            usuario_id=usuario_id,
            estado='aceptado'
        ).first()
        
        if not colaborador:
            return False, False, None
        
        config = {
            'horas_reales_activas': colaborador.horas_reales_activas,
            'rol': colaborador.rol,
        }
        
        return True, colaborador.rol == 'owner', config
