"""
Modelo de Tarifas (Rates)
Sistema de doble estructura: Costo Interno vs Tarifa de Venta
Fase 3: Motor Financiero
"""

from app import db
from datetime import datetime
from enum import Enum
from typing import Optional

class RateType(str, Enum):
    """Tipo de tarifa"""
    PROJECT = 'project'      # Tarifa única por proyecto
    PERSON = 'person'        # Tarifa diferente por persona
    TASK = 'task'           # Tarifa diferente por tipo de tarea
    ROLE = 'role'           # Tarifa por rol organizacional

class Rate(db.Model):
    """
    Modelo de Tarifa
    Almacena tanto costos internos como tarifas de venta
    """
    __tablename__ = 'rates'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    # Tipo de tarifa
    rate_type = db.Column(db.Enum(RateType), nullable=False, default=RateType.PROJECT)
    
    # Referencias opcionales según el tipo
    project_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Para tarifas por persona
    task_type = db.Column(db.String(100), nullable=True)  # Para tarifas por tipo de tarea
    role = db.Column(db.String(50), nullable=True)  # Para tarifas por rol
    
    # Valores monetarios
    internal_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # Lo que GASTAS
    billing_rate = db.Column(db.Numeric(10, 2), nullable=False, default=0)   # Lo que COBRAS
    
    # Metadata
    currency = db.Column(db.String(3), nullable=False, default='USD')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # Relaciones
    organization = db.relationship('Organization', backref='rates')
    project = db.relationship('Proyecto', backref='rates', foreign_keys=[project_id])
    user = db.relationship('Usuario', foreign_keys=[user_id], backref='assigned_rates')
    creator = db.relationship('Usuario', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Rate {self.rate_type.value}: Cost=${self.internal_cost} Bill=${self.billing_rate}>'

    def to_dict(self):
        """Serializa el rate a diccionario"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'rate_type': self.rate_type.value,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'task_type': self.task_type,
            'role': self.role,
            'internal_cost': float(self.internal_cost) if self.internal_cost else 0,
            'billing_rate': float(self.billing_rate) if self.billing_rate else 0,
            'currency': self.currency,
            'is_active': self.is_active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def calculate_margin(self) -> float:
        """Calcula el margen de ganancia en porcentaje"""
        if self.billing_rate == 0:
            return 0
        margin = ((self.billing_rate - self.internal_cost) / self.billing_rate) * 100
        return round(margin, 2)

    def calculate_profit_per_hour(self) -> float:
        """Calcula la ganancia por hora"""
        return float(self.billing_rate - self.internal_cost)

    @staticmethod
    def get_effective_rate(organization_id: int, project_id: Optional[int] = None, 
                          user_id: Optional[int] = None, task_type: Optional[str] = None) -> Optional['Rate']:
        """
        Obtiene la tarifa efectiva según la jerarquía de prioridad:
        1. Tarifa por tarea específica
        2. Tarifa por persona en el proyecto
        3. Tarifa por proyecto
        4. Tarifa por rol del usuario
        """
        query = Rate.query.filter_by(organization_id=organization_id, is_active=True)
        
        # Prioridad 1: Tarifa por tipo de tarea
        if task_type:
            rate = query.filter_by(rate_type=RateType.TASK, task_type=task_type).first()
            if rate:
                return rate
        
        # Prioridad 2: Tarifa por persona
        if user_id and project_id:
            rate = query.filter_by(
                rate_type=RateType.PERSON, 
                user_id=user_id, 
                project_id=project_id
            ).first()
            if rate:
                return rate
        
        # Prioridad 3: Tarifa por proyecto
        if project_id:
            rate = query.filter_by(rate_type=RateType.PROJECT, project_id=project_id).first()
            if rate:
                return rate
        
        # Prioridad 4: Tarifa por rol (fallback)
        if user_id:
            from app.models.organization_member import OrganizationMember
            member = OrganizationMember.query.filter_by(
                organization_id=organization_id, 
                user_id=user_id
            ).first()
            if member:
                rate = query.filter_by(rate_type=RateType.ROLE, role=member.role).first()
                if rate:
                    return rate
        
        return None
