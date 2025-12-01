"""
Modelo de Gastos del Proyecto (Project Expenses)
Gastos no humanos: servidores, licencias, viáticos, etc.
Fase 3: Motor Financiero
"""

from app import db
from datetime import datetime
from enum import Enum

class ExpenseCategory(str, Enum):
    """Categorías de gastos"""
    SOFTWARE = 'software'           # Licencias de software
    HARDWARE = 'hardware'           # Equipos, servidores
    SERVICES = 'services'           # Servicios cloud, hosting
    TRAVEL = 'travel'               # Viáticos, transporte
    MATERIALS = 'materials'         # Materiales físicos
    SUBCONTRACTORS = 'subcontractors'  # Subcontratistas externos
    OTHER = 'other'                 # Otros gastos

class ProjectExpense(db.Model):
    """
    Modelo de Gastos del Proyecto
    Gastos adicionales que no son horas de trabajo
    """
    __tablename__ = 'project_expenses'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=False)
    
    # Información del gasto
    category = db.Column(db.Enum(ExpenseCategory), nullable=False, default=ExpenseCategory.OTHER)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    
    # Fecha y recurrencia
    expense_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    is_recurring = db.Column(db.Boolean, nullable=False, default=False)
    recurrence_frequency = db.Column(db.String(20), nullable=True)  # 'monthly', 'yearly'
    
    # Metadata y documentación
    receipt_url = db.Column(db.String(500), nullable=True)  # URL del recibo/factura
    vendor = db.Column(db.String(200), nullable=True)  # Proveedor
    notes = db.Column(db.Text, nullable=True)
    
    # Aprobación
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Facturación al cliente
    is_billable = db.Column(db.Boolean, nullable=False, default=True)
    is_billed = db.Column(db.Boolean, nullable=False, default=False)
    
    # Timestamps y auditoría
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relaciones
    organization = db.relationship('Organization', backref='project_expenses')
    project = db.relationship('Proyecto', backref='expenses')
    creator = db.relationship('Usuario', foreign_keys=[created_by], backref='created_expenses')
    approver = db.relationship('Usuario', foreign_keys=[approved_by], backref='approved_expenses')

    def __repr__(self):
        return f'<ProjectExpense {self.description}: ${self.amount}>'

    def to_dict(self):
        """Serializa el gasto a diccionario"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'project_id': self.project_id,
            'category': self.category.value,
            'description': self.description,
            'amount': float(self.amount),
            'currency': self.currency,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'is_recurring': self.is_recurring,
            'recurrence_frequency': self.recurrence_frequency,
            'receipt_url': self.receipt_url,
            'vendor': self.vendor,
            'notes': self.notes,
            'is_approved': self.is_approved,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'is_billable': self.is_billable,
            'is_billed': self.is_billed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.nombre if self.creator else None,
            'approver_name': self.approver.nombre if self.approver else None,
        }

    def approve(self, user_id: int) -> None:
        """Aprueba el gasto"""
        self.is_approved = True
        self.approved_by = user_id
        self.approved_at = datetime.utcnow()
        
        # Actualizar el presupuesto del proyecto
        if self.project.budget:
            self.project.budget.add_expense(float(self.amount), self.description)

    @staticmethod
    def get_project_total(project_id: int, category: ExpenseCategory = None) -> float:
        """
        Calcula el total de gastos de un proyecto
        Args:
            project_id: ID del proyecto
            category: Categoría opcional para filtrar
        Returns:
            Total de gastos aprobados
        """
        query = ProjectExpense.query.filter_by(
            project_id=project_id,
            is_approved=True
        )
        
        if category:
            query = query.filter_by(category=category)
        
        expenses = query.all()
        return sum(float(expense.amount) for expense in expenses)

    @staticmethod
    def get_billable_total(project_id: int) -> float:
        """
        Calcula el total de gastos facturables al cliente
        Args:
            project_id: ID del proyecto
        Returns:
            Total de gastos facturables aprobados
        """
        expenses = ProjectExpense.query.filter_by(
            project_id=project_id,
            is_approved=True,
            is_billable=True
        ).all()
        
        return sum(float(expense.amount) for expense in expenses)
