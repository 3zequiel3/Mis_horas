from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class EmpleadoUsuario(db.Model):
    __tablename__ = "empleado_usuario"

    id = db.Column(db.Integer, primary_key=True, index=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=False, unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    
    # Estado de la relación
    estado = db.Column(
        db.Enum('pendiente', 'activo', 'inactivo', name='estado_empleado_usuario_enum'),
        default='activo'
    )
    rol_empleado = db.Column(
        db.Enum('empleado', 'supervisor', name='rol_empleado_enum'),
        default='empleado'
    )
    
    # Permisos específicos del empleado en este proyecto
    puede_ver_otros_empleados = db.Column(db.Boolean, default=False)
    puede_exportar_propio_reporte = db.Column(db.Boolean, default=False)
    
    fecha_asociacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), onupdate=lambda: datetime.now(LOCAL_TZ))

    # Relaciones
    empleado = db.relationship("Empleado", backref="relacion_usuario", uselist=False)
    usuario = db.relationship("Usuario", backref="empleados_asociados")

    def to_dict(self):
        """Convierte la relación a diccionario"""
        return {
            'id': self.id,
            'empleado_id': self.empleado_id,
            'usuario_id': self.usuario_id,
            'estado': self.estado,
            'rol_empleado': self.rol_empleado,
            'puede_ver_otros_empleados': self.puede_ver_otros_empleados,
            'puede_exportar_propio_reporte': self.puede_exportar_propio_reporte,
            'fecha_asociacion': self.fecha_asociacion.isoformat() if self.fecha_asociacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
