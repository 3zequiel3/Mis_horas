from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class ProyectoColaborador(db.Model):
    """
    Colaboradores de un proyecto colaborativo
    Representa usuarios que tienen acceso a un proyecto compartido
    """
    __tablename__ = "proyecto_colaboradores"

    id = db.Column(db.Integer, primary_key=True, index=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Rol del colaborador
    rol = db.Column(
        db.Enum('owner', 'colaborador', name='rol_colaborador_enum'),
        default='colaborador',
        nullable=False
    )
    
    # Configuración individual
    horas_reales_activas = db.Column(db.Boolean, default=False, nullable=False)
    
    # Estado de la colaboración
    estado = db.Column(
        db.Enum('pendiente', 'aceptado', 'rechazado', name='estado_colaborador_enum'),
        default='aceptado',
        nullable=False,
        index=True
    )
    
    # Fechas
    fecha_invitacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_aceptacion = db.Column(db.DateTime, nullable=True)
    fecha_salida = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    proyecto = db.relationship("Proyecto", back_populates="colaboradores")
    usuario = db.relationship("Usuario", backref="proyectos_colaborando")
    
    # Índice compuesto para evitar colaboradores duplicados
    __table_args__ = (
        db.UniqueConstraint('proyecto_id', 'usuario_id', name='unique_proyecto_colaborador'),
        db.Index('idx_proyecto_usuario_estado', 'proyecto_id', 'usuario_id', 'estado'),
    )

    def to_dict(self, incluir_usuario=False, incluir_estadisticas=False):
        """Convierte el colaborador a diccionario"""
        data = {
            'id': self.id,
            'proyecto_id': self.proyecto_id,
            'usuario_id': self.usuario_id,
            'rol': self.rol,
            'horas_reales_activas': self.horas_reales_activas,
            'estado': self.estado,
            'fecha_invitacion': self.fecha_invitacion.isoformat() if self.fecha_invitacion else None,
            'fecha_aceptacion': self.fecha_aceptacion.isoformat() if self.fecha_aceptacion else None,
            'fecha_salida': self.fecha_salida.isoformat() if self.fecha_salida else None,
        }
        
        if incluir_usuario and self.usuario:
            data['usuario'] = {
                'id': self.usuario.id,
                'username': self.usuario.username,
                'email': self.usuario.email,
                'nombre_completo': self.usuario.nombre_completo,
                'foto_perfil': self.usuario.foto_perfil,
            }
        
        if incluir_estadisticas and self.proyecto:
            # Calcular estadísticas de horas del colaborador
            from app.models.dia import Dia
            from app.models.dia_colaborador import DiaColaborador
            from sqlalchemy import func
            
            # En proyectos colaborativos, usar tabla dias_colaboradores
            if self.proyecto.tipo_proyecto == 'colaborativo':
                # Horas desde dias_colaboradores
                total_horas_dc = db.session.query(
                    func.sum(DiaColaborador.horas_trabajadas)
                ).filter(
                    DiaColaborador.usuario_colaborador_id == self.usuario_id
                ).join(
                    Dia, DiaColaborador.dia_id == Dia.id
                ).filter(
                    Dia.proyecto_id == self.proyecto_id
                ).scalar() or 0
                
                total_horas_reales_dc = db.session.query(
                    func.sum(DiaColaborador.horas_reales)
                ).filter(
                    DiaColaborador.usuario_colaborador_id == self.usuario_id
                ).join(
                    Dia, DiaColaborador.dia_id == Dia.id
                ).filter(
                    Dia.proyecto_id == self.proyecto_id
                ).scalar() or 0
                
                # Si es propietario, sumar también horas históricas de dias (pre-conversión)
                if self.rol == 'owner':
                    # IDs de días que ya tienen registro en dias_colaboradores
                    dias_con_registro = db.session.query(DiaColaborador.dia_id).filter(
                        DiaColaborador.usuario_colaborador_id == self.usuario_id
                    ).join(
                        Dia, DiaColaborador.dia_id == Dia.id
                    ).filter(
                        Dia.proyecto_id == self.proyecto_id
                    ).all()
                    dias_con_registro_ids = [d[0] for d in dias_con_registro]
                    
                    # Sumar horas de días sin registro en dias_colaboradores
                    query_historicas = db.session.query(
                        func.sum(Dia.horas_trabajadas),
                        func.sum(Dia.horas_reales)
                    ).filter(
                        Dia.proyecto_id == self.proyecto_id,
                        Dia.empleado_id == None
                    )
                    
                    if dias_con_registro_ids:
                        query_historicas = query_historicas.filter(~Dia.id.in_(dias_con_registro_ids))
                    
                    historicas = query_historicas.first()
                    total_horas_historicas = historicas[0] or 0
                    total_horas_reales_historicas = historicas[1] or 0
                    
                    total_horas = total_horas_dc + total_horas_historicas
                    total_horas_reales = total_horas_reales_dc + total_horas_reales_historicas
                else:
                    total_horas = total_horas_dc
                    total_horas_reales = total_horas_reales_dc
                
            else:
                # Proyectos personales: usar días directamente
                total_horas = db.session.query(
                    func.sum(Dia.horas_trabajadas)
                ).filter(
                    Dia.proyecto_id == self.proyecto_id,
                    Dia.usuario_colaborador_id == None,
                    Dia.empleado_id == None
                ).scalar() or 0
                
                total_horas_reales = db.session.query(
                    func.sum(Dia.horas_reales)
                ).filter(
                    Dia.proyecto_id == self.proyecto_id,
                    Dia.usuario_colaborador_id == None,
                    Dia.empleado_id == None
                ).scalar() or 0
            
            data['estadisticas'] = {
                'total_horas_trabajadas': float(total_horas),
                'total_horas_reales': float(total_horas_reales) if self.horas_reales_activas else None,
            }
        
        return data

    @staticmethod
    def es_colaborador(proyecto_id: int, usuario_id: int) -> bool:
        """Verifica si un usuario es colaborador activo de un proyecto"""
        return ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            usuario_id=usuario_id,
            estado='aceptado'
        ).first() is not None

    @staticmethod
    def es_owner(proyecto_id: int, usuario_id: int) -> bool:
        """Verifica si un usuario es el dueño de un proyecto colaborativo"""
        colaborador = ProyectoColaborador.query.filter_by(
            proyecto_id=proyecto_id,
            usuario_id=usuario_id,
            rol='owner',
            estado='aceptado'
        ).first()
        return colaborador is not None
