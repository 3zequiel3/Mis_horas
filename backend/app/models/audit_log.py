"""
Modelo de Auditoría - Sistema de Logs de Acciones
Registra todas las acciones críticas en el sistema
"""

from app import db
from datetime import datetime
from typing import Optional, Dict, Any
import json


class AuditLog(db.Model):
    """
    Registro de auditoría de acciones en el sistema
    La "Caja Negra" para seguridad jurídica y operativa
    """
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Contexto organizacional
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    
    # Actor (quién hizo la acción)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    user_email = db.Column(db.String(255), nullable=True)  # Respaldo si el usuario es eliminado
    user_role = db.Column(db.String(50), nullable=True)  # Rol en el momento de la acción
    
    # Acción realizada
    action = db.Column(db.String(100), nullable=False)  # Ej: "delete_project", "approve_timesheet"
    action_category = db.Column(db.String(50), nullable=False)  # Ej: "project", "time", "user", "organization"
    
    # Entidad afectada
    resource_type = db.Column(db.String(50), nullable=True)  # Ej: "proyecto", "tarea", "empleado"
    resource_id = db.Column(db.Integer, nullable=True)
    resource_name = db.Column(db.String(255), nullable=True)  # Nombre del recurso para referencia
    
    # Detalles de la acción
    description = db.Column(db.Text, nullable=True)  # Descripción legible
    extra_data = db.Column(db.JSON, nullable=True)  # Datos adicionales en formato JSON
    
    # Valores antes/después (para cambios)
    old_value = db.Column(db.JSON, nullable=True)
    new_value = db.Column(db.JSON, nullable=True)
    
    # Información técnica
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 o IPv6
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Severidad
    severity = db.Column(db.String(20), default='info')  # info, warning, critical
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Índices para búsquedas rápidas
    __table_args__ = (
        db.Index('idx_audit_org_date', 'organization_id', 'created_at'),
        db.Index('idx_audit_user', 'user_id', 'created_at'),
        db.Index('idx_audit_action', 'action', 'created_at'),
        db.Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )
    
    def to_dict(self, include_metadata: bool = True) -> Dict[str, Any]:
        """Convierte el log a diccionario"""
        data = {
            'id': self.id,
            'organization_id': self.organization_id,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'user_role': self.user_role,
            'action': self.action,
            'action_category': self.action_category,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'description': self.description,
            'severity': self.severity,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_metadata:
            data['extra_data'] = self.extra_data
            data['old_value'] = self.old_value
            data['new_value'] = self.new_value
            data['user_agent'] = self.user_agent
        
        return data
    
    @staticmethod
    def log_action(
        organization_id: int,
        user_id: Optional[int],
        action: str,
        action_category: str,
        description: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        resource_name: Optional[str] = None,
        old_value: Optional[Dict] = None,
        new_value: Optional[Dict] = None,
        extra_data: Optional[Dict] = None,
        severity: str = 'info',
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> 'AuditLog':
        """
        Método de conveniencia para crear un log de auditoría
        
        Args:
            organization_id: ID de la organización
            user_id: ID del usuario que realizó la acción
            action: Identificador de la acción (snake_case)
            action_category: Categoría (project, time, user, organization, etc.)
            description: Descripción legible de la acción
            resource_type: Tipo de recurso afectado
            resource_id: ID del recurso afectado
            resource_name: Nombre del recurso para referencia
            old_value: Valor anterior (para updates)
            new_value: Valor nuevo (para updates)
            metadata: Datos adicionales
            severity: Nivel de severidad (info, warning, critical)
            ip_address: IP del usuario
            user_agent: User agent del navegador
            user_email: Email del usuario (respaldo)
            user_role: Rol del usuario en el momento
            
        Returns:
            AuditLog: Instancia del log creado
        """
        log = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=action,
            action_category=action_category,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            description=description,
            extra_data=extra_data,
            old_value=old_value,
            new_value=new_value,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
    
    @staticmethod
    def get_recent_logs(organization_id: int, limit: int = 50, user_id: Optional[int] = None):
        """Obtiene los logs más recientes de una organización"""
        query = AuditLog.query.filter_by(organization_id=organization_id)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def search_logs(
        organization_id: int,
        action: Optional[str] = None,
        action_category: Optional[str] = None,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ):
        """Búsqueda avanzada de logs con filtros"""
        query = AuditLog.query.filter_by(organization_id=organization_id)
        
        if action:
            query = query.filter_by(action=action)
        
        if action_category:
            query = query.filter_by(action_category=action_category)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        
        if severity:
            query = query.filter_by(severity=severity)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()


# Acciones auditables predefinidas
class AuditAction:
    """Constantes para acciones auditables"""
    
    # Organización
    CREATE_ORGANIZATION = "create_organization"
    DELETE_ORGANIZATION = "delete_organization"
    UPDATE_ORGANIZATION = "update_organization"
    TRANSFER_OWNERSHIP = "transfer_ownership"
    CHANGE_PLAN = "change_plan"
    
    # Usuarios
    INVITE_MEMBER = "invite_member"
    REMOVE_MEMBER = "remove_member"
    CHANGE_ROLE = "change_role"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    
    # Proyectos
    CREATE_PROJECT = "create_project"
    DELETE_PROJECT = "delete_project"
    UPDATE_PROJECT = "update_project"
    ARCHIVE_PROJECT = "archive_project"
    
    # Tiempo
    CREATE_TIME_ENTRY = "create_time_entry"
    UPDATE_TIME_ENTRY = "update_time_entry"
    DELETE_TIME_ENTRY = "delete_time_entry"
    SUBMIT_TIMESHEET = "submit_timesheet"
    APPROVE_TIMESHEET = "approve_timesheet"
    REJECT_TIMESHEET = "reject_timesheet"
    REOPEN_TIMESHEET = "reopen_timesheet"
    LOCK_PERIOD = "lock_period"
    
    # Tareas
    CREATE_TASK = "create_task"
    DELETE_TASK = "delete_task"
    UPDATE_TASK = "update_task"
    ASSIGN_TASK = "assign_task"
    
    # Empleados
    ADD_EMPLOYEE = "add_employee"
    REMOVE_EMPLOYEE = "remove_employee"
    UPDATE_EMPLOYEE = "update_employee"
    UPDATE_EMPLOYEE_RATE = "update_employee_rate"
    
    # Financiero
    VIEW_COSTS = "view_costs"
    UPDATE_BUDGET = "update_budget"
    EXPORT_REPORT = "export_report"


class AuditCategory:
    """Categorías de auditoría"""
    ORGANIZATION = "organization"
    USER = "user"
    PROJECT = "project"
    TIME = "time"
    TASK = "task"
    EMPLOYEE = "employee"
    FINANCIAL = "financial"
    SECURITY = "security"
    SYSTEM = "system"
