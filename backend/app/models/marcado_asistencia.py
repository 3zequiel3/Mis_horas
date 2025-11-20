from app import db
from datetime import datetime, timezone, timedelta, time as dt_time

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class MarcadoAsistencia(db.Model):
    __tablename__ = "marcados_asistencia"

    id = db.Column(db.Integer, primary_key=True, index=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=False, index=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False, index=True)
    dia_id = db.Column(db.Integer, db.ForeignKey("dias.id"), nullable=True)
    
    fecha = db.Column(db.Date, nullable=False, index=True)
    
    # Detección de turno
    turno = db.Column(
        db.Enum('manana', 'tarde', 'nocturno', 'especial', name='turno_enum'),
        nullable=True
    )
    
    # Marcados de entrada/salida
    hora_entrada = db.Column(db.Time, nullable=True)
    hora_salida = db.Column(db.Time, nullable=True)
    
    # Estado del marcado
    entrada_marcada_manualmente = db.Column(db.Boolean, default=False)
    salida_marcada_manualmente = db.Column(db.Boolean, default=False)
    salida_marcada_automaticamente = db.Column(db.Boolean, default=False)
    
    # Confirmación de trabajo continuo
    confirmacion_continua = db.Column(db.Boolean, default=False)
    confirmada_por_admin = db.Column(db.Boolean, default=False)
    
    # Cálculos
    horas_trabajadas = db.Column(db.Numeric(5, 2), default=0)
    horas_extras = db.Column(db.Numeric(5, 2), default=0)
    horas_normales = db.Column(db.Numeric(5, 2), default=0)
    
    # Observaciones
    observaciones = db.Column(db.Text, nullable=True)
    
    # Geolocalización (opcional, para futuro)
    latitud_entrada = db.Column(db.Numeric(10, 8), nullable=True)
    longitud_entrada = db.Column(db.Numeric(11, 8), nullable=True)
    latitud_salida = db.Column(db.Numeric(10, 8), nullable=True)
    longitud_salida = db.Column(db.Numeric(11, 8), nullable=True)
    
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), onupdate=lambda: datetime.now(LOCAL_TZ))

    # Relaciones
    empleado = db.relationship("Empleado", backref="marcados_asistencia")
    proyecto = db.relationship("Proyecto", backref="marcados_asistencia")
    dia = db.relationship("Dia", backref="marcado_asistencia")

    def calcular_horas_trabajadas(self):
        """Calcula las horas trabajadas entre entrada y salida"""
        if not self.hora_entrada or not self.hora_salida:
            return 0
        
        # Convertir a datetime para hacer cálculos
        fecha_base = datetime.now(LOCAL_TZ).date()
        entrada_dt = datetime.combine(fecha_base, self.hora_entrada)
        salida_dt = datetime.combine(fecha_base, self.hora_salida)
        
        # Si la salida es antes que la entrada, asumimos que pasó la medianoche
        if salida_dt <= entrada_dt:
            salida_dt += timedelta(days=1)
        
        diferencia = salida_dt - entrada_dt
        return round(diferencia.total_seconds() / 3600, 2)

    def detectar_turno_automatico(self, proyecto):
        """Detecta automáticamente el turno según la hora de entrada"""
        if not self.hora_entrada or not proyecto:
            return None
        
        if proyecto.modo_horarios != 'turnos':
            return None
        
        # Comparar con horarios de turnos
        if proyecto.turno_manana_inicio and proyecto.turno_manana_fin:
            if proyecto.turno_manana_inicio <= self.hora_entrada <= proyecto.turno_manana_fin:
                return 'manana'
        
        if proyecto.turno_tarde_inicio and proyecto.turno_tarde_fin:
            if proyecto.turno_tarde_inicio <= self.hora_entrada <= proyecto.turno_tarde_fin:
                return 'tarde'
        
        return 'especial'

    def to_dict(self):
        """Convierte el marcado a diccionario"""
        return {
            'id': self.id,
            'empleado_id': self.empleado_id,
            'proyecto_id': self.proyecto_id,
            'dia_id': self.dia_id,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'turno': self.turno,
            'hora_entrada': self.hora_entrada.strftime('%H:%M:%S') if self.hora_entrada else None,
            'hora_salida': self.hora_salida.strftime('%H:%M:%S') if self.hora_salida else None,
            'entrada_marcada_manualmente': self.entrada_marcada_manualmente,
            'salida_marcada_manualmente': self.salida_marcada_manualmente,
            'salida_marcada_automaticamente': self.salida_marcada_automaticamente,
            'confirmacion_continua': self.confirmacion_continua,
            'confirmada_por_admin': self.confirmada_por_admin,
            'horas_trabajadas': float(self.horas_trabajadas) if self.horas_trabajadas else 0,
            'horas_extras': float(self.horas_extras) if self.horas_extras else 0,
            'horas_normales': float(self.horas_normales) if self.horas_normales else 0,
            'observaciones': self.observaciones,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
