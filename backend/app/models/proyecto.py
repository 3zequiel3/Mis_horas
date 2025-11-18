from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class Proyecto(db.Model):
    __tablename__ = "proyectos"

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    anio = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    tipo_proyecto = db.Column(db.String(50), default='personal', nullable=False)  # 'personal' o 'empleados'
    horas_reales_activas = db.Column(db.Boolean, default=False)  # Activar/desactivar horas reales
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), onupdate=lambda: datetime.now(LOCAL_TZ))

    # Relaciones
    usuario = db.relationship("Usuario", back_populates="proyectos")
    dias = db.relationship("Dia", back_populates="proyecto", cascade="all, delete-orphan")
    tareas = db.relationship("Tarea", back_populates="proyecto", cascade="all, delete-orphan")
    empleados = db.relationship("Empleado", back_populates="proyecto", cascade="all, delete-orphan")

    def to_dict(self):
        """Convierte el proyecto a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'anio': self.anio,
            'mes': self.mes,
            'usuario_id': self.usuario_id,
            'activo': self.activo,
            'tipo_proyecto': self.tipo_proyecto,
            'horas_reales_activas': self.horas_reales_activas,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'empleados': [e.to_dict() for e in self.empleados] if self.tipo_proyecto == 'empleados' else [],
        }
