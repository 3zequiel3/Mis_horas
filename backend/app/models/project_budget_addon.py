"""
Modelo ProjectBudgetAddon
Adicionales de presupuesto para proyectos
Fase 4: UX Unificada & Gestión Financiera
"""

from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local
LOCAL_TZ = timezone(timedelta(hours=-3))

class ProjectBudgetAddon(db.Model):
    """
    Adicionales de presupuesto
    Permite ampliar el presupuesto base sin modificar el original
    Ejemplo: "Fase 2 Extra", "Soporte Adicional Diciembre"
    """
    __tablename__ = "project_budget_addons"

    id = db.Column(db.Integer, primary_key=True, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("proyectos.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Datos del adicional
    name = db.Column(db.String(255), nullable=False)  # "Fase 2", "Soporte Extra"
    description = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)  # Monto adicional (dinero u horas según budget_type del proyecto)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), onupdate=lambda: datetime.now(LOCAL_TZ))
    
    # Relaciones
    project = db.relationship("Proyecto", backref="budget_addons")
    organization = db.relationship("Organization", backref="project_budget_addons")
    creator = db.relationship("Usuario", backref="created_budget_addons")
    
    def to_dict(self):
        """Convierte el adicional a diccionario"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'organization_id': self.organization_id,
            'name': self.name,
            'description': self.description,
            'amount': float(self.amount),
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @staticmethod
    def get_project_total_addons(project_id: int) -> float:
        """
        Obtiene la suma total de todos los adicionales de un proyecto
        """
        total = db.session.query(
            db.func.sum(ProjectBudgetAddon.amount)
        ).filter(
            ProjectBudgetAddon.project_id == project_id
        ).scalar()
        
        return float(total) if total else 0.0
    
    @staticmethod
    def calculate_total_budget(project_id: int, base_amount: float) -> float:
        """
        Calcula el presupuesto total (base + adicionales)
        """
        addons_total = ProjectBudgetAddon.get_project_total_addons(project_id)
        return base_amount + addons_total
    
    def __repr__(self):
        return f"<ProjectBudgetAddon {self.id}: {self.name} (${self.amount})>"
