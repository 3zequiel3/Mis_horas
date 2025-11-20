from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class Justificacion(db.Model):
    __tablename__ = "justificaciones"

    id = db.Column(db.Integer, primary_key=True, index=True)
    deuda_id = db.Column(db.Integer, db.ForeignKey("deudas_horas.id"), nullable=False, index=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=False, index=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False)
    
    # Detalles de la justificación
    motivo = db.Column(db.Text, nullable=False)
    horas_a_justificar = db.Column(db.Numeric(5, 2), nullable=False)
    
    # Archivos adjuntos
    archivo_url = db.Column(db.String(500), nullable=True)
    archivo_nombre = db.Column(db.String(255), nullable=True)
    archivo_tipo = db.Column(db.String(100), nullable=True)
    archivo_tamano = db.Column(db.Integer, nullable=True)  # Tamaño en bytes
    
    # Estado de aprobación
    estado = db.Column(
        db.Enum('pendiente', 'aprobada', 'rechazada', name='estado_justificacion_enum'),
        default='pendiente',
        index=True
    )
    
    # Revisión del admin
    revisada_por_usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    fecha_revision = db.Column(db.DateTime, nullable=True)
    comentario_admin = db.Column(db.Text, nullable=True)
    
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), onupdate=lambda: datetime.now(LOCAL_TZ))

    # Relaciones
    deuda = db.relationship("DeudaHoras", back_populates="justificaciones")
    empleado = db.relationship("Empleado", backref="justificaciones")
    proyecto = db.relationship("Proyecto", backref="justificaciones")
    revisada_por = db.relationship("Usuario", backref="justificaciones_revisadas")

    def aprobar(self, usuario_id, comentario=None):
        """Aprueba la justificación"""
        self.estado = 'aprobada'
        self.revisada_por_usuario_id = usuario_id
        self.fecha_revision = datetime.now(LOCAL_TZ)
        self.comentario_admin = comentario
        
        # Actualizar las horas justificadas en la deuda
        self.deuda.horas_justificadas = float(self.deuda.horas_justificadas or 0) + float(self.horas_a_justificar)
        
        # Si la deuda quedó totalmente justificada, cambiar estado
        if self.deuda.horas_pendientes <= 0:
            self.deuda.estado = 'justificada'
        
        db.session.commit()

    def rechazar(self, usuario_id, comentario):
        """Rechaza la justificación"""
        self.estado = 'rechazada'
        self.revisada_por_usuario_id = usuario_id
        self.fecha_revision = datetime.now(LOCAL_TZ)
        self.comentario_admin = comentario
        db.session.commit()

    def to_dict(self):
        """Convierte la justificación a diccionario"""
        return {
            'id': self.id,
            'deuda_id': self.deuda_id,
            'empleado_id': self.empleado_id,
            'proyecto_id': self.proyecto_id,
            'motivo': self.motivo,
            'horas_a_justificar': float(self.horas_a_justificar) if self.horas_a_justificar else 0,
            'archivo_url': self.archivo_url,
            'archivo_nombre': self.archivo_nombre,
            'archivo_tipo': self.archivo_tipo,
            'archivo_tamano': self.archivo_tamano,
            'estado': self.estado,
            'revisada_por_usuario_id': self.revisada_por_usuario_id,
            'fecha_revision': self.fecha_revision.isoformat() if self.fecha_revision else None,
            'comentario_admin': self.comentario_admin,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
