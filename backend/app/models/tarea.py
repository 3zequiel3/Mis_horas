from app import db
from app.models.dia import tarea_dia

class Tarea(db.Model):
    __tablename__ = "tareas"

    id = db.Column(db.Integer, primary_key=True, index=True)
    titulo = db.Column(db.String(255), nullable=False)
    detalle = db.Column(db.Text, nullable=True)
    horas = db.Column(db.String(50), default="")
    que_falta = db.Column(db.Text, nullable=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False)

    proyecto = db.relationship("Proyecto", back_populates="tareas")
    dias = db.relationship("Dia", secondary=tarea_dia, back_populates="tareas")

    def to_dict(self):
        """Convierte la tarea a diccionario"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'detalle': self.detalle,
            'horas': self.horas,
            'que_falta': self.que_falta,
            'proyecto_id': self.proyecto_id,
            'dias': [dia.to_dict() for dia in self.dias],
        }
