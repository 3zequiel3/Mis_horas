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
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)

    # Relaciones
    proyecto = db.relationship("Proyecto", back_populates="empleados")
    dias = db.relationship("Dia", back_populates="empleado", cascade="all, delete-orphan")

    def to_dict(self):
        """Convierte el empleado a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'proyecto_id': self.proyecto_id,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
