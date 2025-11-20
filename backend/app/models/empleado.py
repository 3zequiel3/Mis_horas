from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class Empleado(db.Model):
    __tablename__ = "empleados"

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(255), nullable=False)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    # Relación con usuario del sistema (nuevo)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    estado_asistencia = db.Column(
        db.Enum('activo', 'inactivo', 'suspendido', name='estado_asistencia_enum'),
        default='activo'
    )
    
    # Horarios especiales individuales (sobrescriben los del proyecto si están activos)
    horario_especial_inicio = db.Column(db.Time, nullable=True)
    horario_especial_fin = db.Column(db.Time, nullable=True)
    usa_horario_especial = db.Column(db.Boolean, default=False)
    
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)

    # Relaciones
    proyecto = db.relationship("Proyecto", back_populates="empleados")
    dias = db.relationship("Dia", back_populates="empleado", cascade="all, delete-orphan")
    usuario_asociado = db.relationship("Usuario", foreign_keys=[usuario_id], backref="empleados_directos")

    def to_dict(self, incluir_usuario=False):
        """Convierte el empleado a diccionario"""
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'proyecto_id': self.proyecto_id,
            'activo': self.activo,
            'usuario_id': self.usuario_id,
            'estado_asistencia': self.estado_asistencia,
            'horario_especial_inicio': self.horario_especial_inicio.strftime('%H:%M') if self.horario_especial_inicio else None,
            'horario_especial_fin': self.horario_especial_fin.strftime('%H:%M') if self.horario_especial_fin else None,
            'usa_horario_especial': self.usa_horario_especial,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
        
        # Incluir datos del usuario asociado si se solicita
        if incluir_usuario and self.usuario_asociado:
            data['usuario'] = {
                'id': self.usuario_asociado.id,
                'username': self.usuario_asociado.username,
                'email': self.usuario_asociado.email,
                'nombre_completo': self.usuario_asociado.nombre_completo,
            }
        
        return data
