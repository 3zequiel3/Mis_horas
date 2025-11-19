from app import db

# Tabla de asociación muchos-a-muchos
tarea_dia = db.Table(
    'tarea_dia',
    db.Column('tarea_id', db.Integer, db.ForeignKey('tareas.id'), primary_key=True),
    db.Column('dia_id', db.Integer, db.ForeignKey('dias.id'), primary_key=True)
)

class Dia(db.Model):
    __tablename__ = "dias"

    id = db.Column(db.Integer, primary_key=True, index=True)
    fecha = db.Column(db.Date, nullable=False, index=True)
    dia_semana = db.Column(db.String(20), nullable=False)
    horas_trabajadas = db.Column(db.Float, default=0)
    horas_reales = db.Column(db.Float, default=0)
    hora_entrada = db.Column(db.Time, nullable=True)  # Nueva columna para hora de entrada
    hora_salida = db.Column(db.Time, nullable=True)   # Nueva columna para hora de salida
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False)
    empleado_id = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=True)  # Null para proyectos personales

    proyecto = db.relationship("Proyecto", back_populates="dias")
    empleado = db.relationship("Empleado", back_populates="dias")
    tareas = db.relationship("Tarea", secondary=tarea_dia, back_populates="dias")

    def to_dict(self):
        """Convierte el día a diccionario"""
        return {
            'id': self.id,
            'fecha': self.fecha.isoformat(),
            'dia_semana': self.dia_semana,
            'horas_trabajadas': self.horas_trabajadas,
            'horas_reales': self.horas_reales,
            'hora_entrada': self.hora_entrada.strftime('%H:%M') if self.hora_entrada else None,
            'hora_salida': self.hora_salida.strftime('%H:%M') if self.hora_salida else None,
            'proyecto_id': self.proyecto_id,
            'empleado_id': self.empleado_id,
        }
