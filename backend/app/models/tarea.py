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

    def to_dict(self, incluir_desglose_empleados=False):
        """Convierte la tarea a diccionario"""
        result = {
            'id': self.id,
            'titulo': self.titulo,
            'detalle': self.detalle,
            'horas': self.horas,
            'que_falta': self.que_falta,
            'proyecto_id': self.proyecto_id,
            'dias': [dia.to_dict() for dia in self.dias],
        }
        
        # Si se solicita y es proyecto de empleados, agregar desglose
        if incluir_desglose_empleados and self.proyecto and self.proyecto.tipo_proyecto == 'empleados':
            desglose = {}
            for dia in self.dias:
                if dia.empleado_id:
                    empleado_nombre = dia.empleado.nombre if dia.empleado else f"Empleado {dia.empleado_id}"
                    if empleado_nombre not in desglose:
                        desglose[empleado_nombre] = {
                            'empleado_id': dia.empleado_id,
                            'empleado_nombre': empleado_nombre,
                            'horas_totales': 0,
                            'dias_count': 0
                        }
                    desglose[empleado_nombre]['horas_totales'] += dia.horas_trabajadas or 0
                    desglose[empleado_nombre]['dias_count'] += 1
            
            result['desglose_empleados'] = list(desglose.values())
        
        return result
