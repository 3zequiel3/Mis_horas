from app import db

class DiaColaborador(db.Model):
    """
    Horas de cada colaborador en cada día (proyectos colaborativos)
    Permite que múltiples colaboradores tengan diferentes horas en el mismo día
    """
    __tablename__ = "dias_colaboradores"

    id = db.Column(db.Integer, primary_key=True, index=True)
    dia_id = db.Column(db.Integer, db.ForeignKey("dias.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_colaborador_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    horas_trabajadas = db.Column(db.Float, default=0)
    horas_reales = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relaciones
    dia = db.relationship("Dia", backref="horas_colaboradores")
    usuario = db.relationship("Usuario", foreign_keys=[usuario_colaborador_id])
    
    # Constraint único: un colaborador solo tiene un registro por día
    __table_args__ = (
        db.UniqueConstraint('dia_id', 'usuario_colaborador_id', name='unique_dia_colaborador'),
    )
    
    def to_dict(self):
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'dia_id': self.dia_id,
            'usuario_colaborador_id': self.usuario_colaborador_id,
            'horas_trabajadas': self.horas_trabajadas,
            'horas_reales': self.horas_reales,
        }
