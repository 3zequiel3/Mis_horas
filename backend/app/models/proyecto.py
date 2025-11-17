from app import db

class Proyecto(db.Model):
    __tablename__ = "proyectos"

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    anio = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    usuario = db.relationship("Usuario", back_populates="proyectos")
    dias = db.relationship("Dia", back_populates="proyecto", cascade="all, delete-orphan")
    tareas = db.relationship("Tarea", back_populates="proyecto", cascade="all, delete-orphan")

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
        }
