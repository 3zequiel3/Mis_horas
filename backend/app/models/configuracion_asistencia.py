from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class ConfiguracionAsistencia(db.Model):
    __tablename__ = "configuracion_asistencia"

    id = db.Column(db.Integer, primary_key=True, index=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False, unique=True)
    
    # Activación del sistema
    modo_asistencia_activo = db.Column(db.Boolean, default=False)
    
    # Políticas de gestión de horas extras vs deudas
    politica_horas_extras = db.Column(
        db.Enum('compensar_deuda', 'bloquear_extras', 'separar_cuentas', name='politica_horas_extras_enum'),
        default='compensar_deuda',
        nullable=False
    )
    
    # Configuración de tolerancias
    tolerancia_retraso_minutos = db.Column(db.Integer, default=15)
    marcar_salida_automatica = db.Column(db.Boolean, default=True)
    
    # Configuración de justificaciones
    permitir_justificaciones = db.Column(db.Boolean, default=True)
    requiere_aprobacion_justificaciones = db.Column(db.Boolean, default=True)
    limite_horas_justificables = db.Column(db.Integer, nullable=True)  # NULL = sin límite
    periodo_limite_justificaciones = db.Column(
        db.Enum('diario', 'semanal', 'mensual', 'anual', name='periodo_limite_enum'),
        default='mensual'
    )
    
    # Notificaciones y recordatorios
    enviar_recordatorio_marcado = db.Column(db.Boolean, default=True)
    enviar_alerta_deuda = db.Column(db.Boolean, default=True)
    hora_recordatorio_entrada = db.Column(db.Time, default=lambda: datetime.strptime('09:00', '%H:%M').time())
    hora_recordatorio_salida = db.Column(db.Time, default=lambda: datetime.strptime('18:00', '%H:%M').time())
    
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), onupdate=lambda: datetime.now(LOCAL_TZ))

    # Relaciones
    proyecto = db.relationship("Proyecto", backref="configuracion_asistencia", uselist=False)

    def to_dict(self):
        """Convierte la configuración a diccionario"""
        return {
            'id': self.id,
            'proyecto_id': self.proyecto_id,
            'modo_asistencia_activo': self.modo_asistencia_activo,
            'politica_horas_extras': self.politica_horas_extras,
            'tolerancia_retraso_minutos': self.tolerancia_retraso_minutos,
            'marcar_salida_automatica': self.marcar_salida_automatica,
            'permitir_justificaciones': self.permitir_justificaciones,
            'requiere_aprobacion_justificaciones': self.requiere_aprobacion_justificaciones,
            'limite_horas_justificables': self.limite_horas_justificables,
            'periodo_limite_justificaciones': self.periodo_limite_justificaciones,
            'enviar_recordatorio_marcado': self.enviar_recordatorio_marcado,
            'enviar_alerta_deuda': self.enviar_alerta_deuda,
            'hora_recordatorio_entrada': self.hora_recordatorio_entrada.strftime('%H:%M') if self.hora_recordatorio_entrada else None,
            'hora_recordatorio_salida': self.hora_recordatorio_salida.strftime('%H:%M') if self.hora_recordatorio_salida else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
