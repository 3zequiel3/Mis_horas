"""
Modelo de Período de Tiempo (Time Period)
Sistema de aprobación y bloqueo de registros de tiempo
"""

from app import db
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from sqlalchemy import and_, or_


class TimePeriodStatus:
    """Estados de un período de tiempo"""
    DRAFT = "draft"  # Borrador - Editable
    PENDING = "pending"  # Pendiente de aprobación - No editable
    APPROVED = "approved"  # Aprobado - Bloqueado
    REJECTED = "rejected"  # Rechazado - Editable con correcciones
    LOCKED = "locked"  # Bloqueado permanentemente - Solo Owner/Admin puede reabrir


class TimePeriod(db.Model):
    """
    Período de tiempo para aprobación
    Agrupa registros de tiempo de un empleado en un período específico
    """
    __tablename__ = 'time_periods'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Contexto organizacional
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id', ondelete='CASCADE'), nullable=False)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id', ondelete='CASCADE'), nullable=False)
    
    # Período
    anio = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=True)  # Opcional: para períodos semanales
    fecha_fin = db.Column(db.Date, nullable=True)
    
    # Estado y aprobación
    status = db.Column(db.String(20), default=TimePeriodStatus.DRAFT, nullable=False)
    
    # Quien envió para aprobación
    submitted_by = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)
    
    # Quien aprobó/rechazó
    reviewed_by = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)  # Notas del revisor
    
    # Estadísticas del período
    total_hours = db.Column(db.Float, default=0.0)
    total_days = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    proyecto = db.relationship('Proyecto', backref='time_periods')
    empleado = db.relationship('Empleado', backref='time_periods')
    
    __table_args__ = (
        db.Index('idx_time_period_org', 'organization_id', 'status'),
        db.Index('idx_time_period_employee', 'empleado_id', 'anio', 'mes'),
        db.Index('idx_time_period_project', 'proyecto_id', 'status'),
        db.UniqueConstraint('proyecto_id', 'empleado_id', 'anio', 'mes', name='uq_period_employee_month'),
    )
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """Convierte el período a diccionario"""
        data = {
            'id': self.id,
            'organization_id': self.organization_id,
            'proyecto_id': self.proyecto_id,
            'empleado_id': self.empleado_id,
            'anio': self.anio,
            'mes': self.mes,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'status': self.status,
            'total_hours': self.total_hours,
            'total_days': self.total_days,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_details:
            data['review_notes'] = self.review_notes
            data['submitted_by'] = self.submitted_by
            data['reviewed_by'] = self.reviewed_by
        
        return data
    
    def can_edit(self) -> bool:
        """Verifica si el período puede ser editado"""
        return self.status in [TimePeriodStatus.DRAFT, TimePeriodStatus.REJECTED]
    
    def can_submit(self) -> bool:
        """Verifica si el período puede ser enviado para aprobación"""
        return self.status == TimePeriodStatus.DRAFT and self.total_hours > 0
    
    def can_approve(self) -> bool:
        """Verifica si el período puede ser aprobado"""
        return self.status == TimePeriodStatus.PENDING
    
    def can_reopen(self) -> bool:
        """Verifica si el período puede ser reabierto"""
        return self.status in [TimePeriodStatus.APPROVED, TimePeriodStatus.LOCKED]
    
    @staticmethod
    def get_or_create_period(
        organization_id: int,
        proyecto_id: int,
        empleado_id: int,
        anio: int,
        mes: int
    ) -> 'TimePeriod':
        """Obtiene o crea un período de tiempo"""
        period = TimePeriod.query.filter_by(
            organization_id=organization_id,
            proyecto_id=proyecto_id,
            empleado_id=empleado_id,
            anio=anio,
            mes=mes
        ).first()
        
        if not period:
            # Calcular fechas del mes
            from calendar import monthrange
            last_day = monthrange(anio, mes)[1]
            
            period = TimePeriod(
                organization_id=organization_id,
                proyecto_id=proyecto_id,
                empleado_id=empleado_id,
                anio=anio,
                mes=mes,
                fecha_inicio=date(anio, mes, 1),
                fecha_fin=date(anio, mes, last_day),
                status=TimePeriodStatus.DRAFT
            )
            db.session.add(period)
            db.session.commit()
        
        return period
    
    def submit_for_approval(self, submitted_by: int) -> bool:
        """Envía el período para aprobación"""
        if not self.can_submit():
            return False
        
        self.status = TimePeriodStatus.PENDING
        self.submitted_by = submitted_by
        self.submitted_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    def approve(self, reviewed_by: int, notes: Optional[str] = None) -> bool:
        """Aprueba el período"""
        if not self.can_approve():
            return False
        
        self.status = TimePeriodStatus.APPROVED
        self.reviewed_by = reviewed_by
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes
        db.session.commit()
        
        return True
    
    def reject(self, reviewed_by: int, notes: str) -> bool:
        """Rechaza el período con notas explicativas"""
        if not self.can_approve():
            return False
        
        self.status = TimePeriodStatus.REJECTED
        self.reviewed_by = reviewed_by
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes
        db.session.commit()
        
        return True
    
    def reopen(self, user_id: int, reason: str) -> bool:
        """Reabre un período aprobado o bloqueado"""
        if not self.can_reopen():
            return False
        
        old_status = self.status
        self.status = TimePeriodStatus.DRAFT
        self.review_notes = f"Reabierto: {reason} (Estado anterior: {old_status})"
        db.session.commit()
        
        return True
    
    def lock(self) -> bool:
        """Bloquea permanentemente el período"""
        if self.status != TimePeriodStatus.APPROVED:
            return False
        
        self.status = TimePeriodStatus.LOCKED
        db.session.commit()
        
        return True
    
    def update_totals(self, total_hours: float, total_days: int):
        """Actualiza los totales del período"""
        self.total_hours = total_hours
        self.total_days = total_days
        db.session.commit()
    
    @staticmethod
    def get_pending_for_review(organization_id: int, reviewer_id: Optional[int] = None):
        """Obtiene períodos pendientes de revisión"""
        query = TimePeriod.query.filter_by(
            organization_id=organization_id,
            status=TimePeriodStatus.PENDING
        )
        
        return query.order_by(TimePeriod.submitted_at.asc()).all()
    
    @staticmethod
    def get_employee_periods(
        organization_id: int,
        empleado_id: int,
        anio: Optional[int] = None,
        mes: Optional[int] = None
    ):
        """Obtiene períodos de un empleado"""
        query = TimePeriod.query.filter_by(
            organization_id=organization_id,
            empleado_id=empleado_id
        )
        
        if anio:
            query = query.filter_by(anio=anio)
        
        if mes:
            query = query.filter_by(mes=mes)
        
        return query.order_by(TimePeriod.anio.desc(), TimePeriod.mes.desc()).all()


# Agregar campo de estado al modelo Dia
def add_status_to_dia():
    """
    Nota: Agregar esta columna al modelo Dia existente:
    
    status = db.Column(db.String(20), default='draft', nullable=False)
    time_period_id = db.Column(db.Integer, db.ForeignKey('time_periods.id'), nullable=True)
    
    Esto permite asociar cada día a un período y heredar su estado
    """
    pass
