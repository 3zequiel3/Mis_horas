from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class DeudaHoras(db.Model):
    __tablename__ = "deudas_horas"

    id = db.Column(db.Integer, primary_key=True, index=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=False, index=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False, index=True)
    
    fecha_inicio = db.Column(db.Date, nullable=False, index=True)
    fecha_fin = db.Column(db.Date, nullable=True)  # NULL si es deuda actual
    
    # Detalles de la deuda
    horas_debidas = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    horas_justificadas = db.Column(db.Numeric(5, 2), default=0)
    horas_compensadas = db.Column(db.Numeric(5, 2), default=0)
    
    # Estado
    estado = db.Column(
        db.Enum('activa', 'justificada', 'compensada', 'cerrada', name='estado_deuda_enum'),
        default='activa',
        index=True
    )
    
    # Motivo automático
    motivo = db.Column(
        db.Enum('ausencia', 'salida_temprana', 'entrada_tardia', 'otro', name='motivo_deuda_enum'),
        nullable=False
    )
    descripcion_automatica = db.Column(db.Text, nullable=True)
    
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), onupdate=lambda: datetime.now(LOCAL_TZ))

    # Relaciones
    empleado = db.relationship("Empleado", backref="deudas_horas")
    proyecto = db.relationship("Proyecto", backref="deudas_horas")
    justificaciones = db.relationship("Justificacion", back_populates="deuda", cascade="all, delete-orphan")

    @property
    def horas_pendientes(self):
        """Calcula las horas pendientes de pagar"""
        debidas = float(self.horas_debidas) if self.horas_debidas else 0
        justificadas = float(self.horas_justificadas) if self.horas_justificadas else 0
        compensadas = float(self.horas_compensadas) if self.horas_compensadas else 0
        return round(debidas - justificadas - compensadas, 2)

    def compensar_con_horas_extras(self, horas_extras):
        """Compensa la deuda con horas extras trabajadas"""
        pendientes = self.horas_pendientes
        if pendientes <= 0:
            return 0  # No hay nada que compensar
        
        horas_a_compensar = min(pendientes, horas_extras)
        self.horas_compensadas = float(self.horas_compensadas or 0) + horas_a_compensar
        
        # Si la deuda quedó totalmente compensada, cambiar estado
        if self.horas_pendientes <= 0:
            self.estado = 'compensada'
        
        db.session.commit()
        return horas_extras - horas_a_compensar  # Retorna las horas extras que sobran

    def to_dict(self):
        """Convierte la deuda a diccionario"""
        return {
            'id': self.id,
            'empleado_id': self.empleado_id,
            'proyecto_id': self.proyecto_id,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'horas_debidas': float(self.horas_debidas) if self.horas_debidas else 0,
            'horas_justificadas': float(self.horas_justificadas) if self.horas_justificadas else 0,
            'horas_compensadas': float(self.horas_compensadas) if self.horas_compensadas else 0,
            'horas_pendientes': self.horas_pendientes,
            'estado': self.estado,
            'motivo': self.motivo,
            'descripcion_automatica': self.descripcion_automatica,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
