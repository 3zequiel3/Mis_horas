"""
Modelo de Presupuesto (Budget)
Gestión de límites de gasto y tracking de consumo
Fase 3: Motor Financiero
"""

from app import db
from datetime import datetime
from enum import Enum
from typing import Optional
from decimal import Decimal

class BudgetType(str, Enum):
    """Tipo de presupuesto"""
    NONE = 'none'           # Sin límite (Pay as you go)
    MONETARY = 'monetary'   # Presupuesto en dinero ($10,000)
    HOURS = 'hours'         # Bolsa de horas (100 horas)
    FIXED_PRICE = 'fixed'   # Precio fijo del proyecto

class Budget(db.Model):
    """
    Modelo de Presupuesto del Proyecto
    Maneja tanto límites monetarios como de horas
    """
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=False, unique=True)
    
    # Tipo y valores
    budget_type = db.Column(db.Enum(BudgetType), nullable=False, default=BudgetType.NONE)
    total_amount = db.Column(db.Numeric(12, 2), nullable=True)  # Presupuesto total en dinero
    total_hours = db.Column(db.Numeric(10, 2), nullable=True)   # Presupuesto total en horas
    currency = db.Column(db.String(3), nullable=False, default='USD')
    
    # Consumo actual (se actualiza automáticamente)
    consumed_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)  # Dinero gastado
    consumed_hours = db.Column(db.Numeric(10, 2), nullable=False, default=0)   # Horas consumidas
    
    # Gastos adicionales (no humanos)
    additional_expenses = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    
    # Configuración de alertas
    alert_threshold_percentage = db.Column(db.Integer, nullable=False, default=80)  # Alertar al 80%
    alert_sent = db.Column(db.Boolean, nullable=False, default=False)
    
    # Estado
    is_exceeded = db.Column(db.Boolean, nullable=False, default=False)
    is_locked = db.Column(db.Boolean, nullable=False, default=False)
    
    # Metadata
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    organization = db.relationship('Organization', backref='budgets')
    project = db.relationship('Proyecto', backref='budget', uselist=False)

    def __repr__(self):
        return f'<Budget Project#{self.project_id} Type={self.budget_type.value}>'

    def to_dict(self):
        """Serializa el presupuesto a diccionario"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'project_id': self.project_id,
            'budget_type': self.budget_type.value,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'total_hours': float(self.total_hours) if self.total_hours else None,
            'currency': self.currency,
            'consumed_amount': float(self.consumed_amount),
            'consumed_hours': float(self.consumed_hours),
            'additional_expenses': float(self.additional_expenses),
            'alert_threshold_percentage': self.alert_threshold_percentage,
            'alert_sent': self.alert_sent,
            'is_exceeded': self.is_exceeded,
            'is_locked': self.is_locked,
            'burn_rate': self.calculate_burn_rate(),
            'remaining': self.calculate_remaining(),
            'health_status': self.get_health_status(),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def calculate_burn_rate(self) -> float:
        """
        Calcula el porcentaje de consumo del presupuesto
        Returns: 0-100 (porcentaje)
        """
        if self.budget_type == BudgetType.NONE:
            return 0
        
        if self.budget_type == BudgetType.HOURS:
            if not self.total_hours or self.total_hours == 0:
                return 0
            return min(100, (float(self.consumed_hours) / float(self.total_hours)) * 100)
        
        # MONETARY o FIXED_PRICE
        total = float(self.total_amount or 0) + float(self.additional_expenses)
        if total == 0:
            return 0
        return min(100, (float(self.consumed_amount) / total) * 100)

    def calculate_remaining(self) -> dict:
        """
        Calcula lo que queda del presupuesto
        Returns: {'amount': float, 'hours': float, 'percentage': float}
        """
        if self.budget_type == BudgetType.NONE:
            return {'amount': None, 'hours': None, 'percentage': 100}
        
        remaining_hours = None
        remaining_amount = None
        
        if self.budget_type == BudgetType.HOURS:
            remaining_hours = max(0, float(self.total_hours or 0) - float(self.consumed_hours))
        else:
            total = float(self.total_amount or 0)
            consumed = float(self.consumed_amount) + float(self.additional_expenses)
            remaining_amount = max(0, total - consumed)
        
        burn_rate = self.calculate_burn_rate()
        remaining_percentage = max(0, 100 - burn_rate)
        
        return {
            'amount': remaining_amount,
            'hours': remaining_hours,
            'percentage': round(remaining_percentage, 2)
        }

    def get_health_status(self) -> str:
        """
        Determina el estado de salud del presupuesto
        Returns: 'healthy', 'warning', 'critical', 'exceeded'
        """
        if self.is_exceeded or self.calculate_burn_rate() >= 100:
            return 'exceeded'
        
        burn_rate = self.calculate_burn_rate()
        
        if burn_rate < 60:
            return 'healthy'
        elif burn_rate < 85:
            return 'warning'
        else:
            return 'critical'

    def should_send_alert(self) -> bool:
        """Verifica si se debe enviar una alerta"""
        if self.alert_sent:
            return False
        
        burn_rate = self.calculate_burn_rate()
        return burn_rate >= self.alert_threshold_percentage

    def add_time_consumption(self, hours: float, cost: float) -> None:
        """
        Agrega consumo de tiempo al presupuesto
        Args:
            hours: Horas trabajadas
            cost: Costo interno de esas horas
        """
        self.consumed_hours = Decimal(str(float(self.consumed_hours) + hours))
        self.consumed_amount = Decimal(str(float(self.consumed_amount) + cost))
        
        # Verificar si se excedió
        if self.budget_type == BudgetType.HOURS:
            self.is_exceeded = float(self.consumed_hours) >= float(self.total_hours or 0)
        elif self.budget_type in [BudgetType.MONETARY, BudgetType.FIXED_PRICE]:
            total = float(self.total_amount or 0)
            self.is_exceeded = float(self.consumed_amount) >= total
        
        # Verificar si enviar alerta
        if self.should_send_alert():
            self.alert_sent = True

    def add_expense(self, amount: float, description: str = None) -> None:
        """
        Agrega un gasto adicional (no humano)
        Args:
            amount: Monto del gasto
            description: Descripción opcional
        """
        self.additional_expenses = Decimal(str(float(self.additional_expenses) + amount))
        
        # Verificar si se excedió
        if self.budget_type in [BudgetType.MONETARY, BudgetType.FIXED_PRICE]:
            total = float(self.total_amount or 0)
            consumed_total = float(self.consumed_amount) + float(self.additional_expenses)
            self.is_exceeded = consumed_total >= total

    def reset_consumption(self) -> None:
        """Resetea el consumo (útil para nuevos períodos)"""
        self.consumed_amount = Decimal('0')
        self.consumed_hours = Decimal('0')
        self.additional_expenses = Decimal('0')
        self.is_exceeded = False
        self.alert_sent = False
