"""
Servicio de Auditoría
Gestión de logs y acciones auditables
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from flask import request
from app.models import AuditLog, AuditAction, AuditCategory
from app import db


class AuditService:
    """Servicio para gestión de auditoría"""
    
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
        user_email: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> AuditLog:
        """
        Registra una acción en el log de auditoría
        Captura automáticamente IP y User Agent del request
        """
        ip_address = None
        user_agent = None
        
        # Capturar IP y User Agent del request si está disponible
        if request:
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')[:500]
        
        return AuditLog.log_action(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            action_category=action_category,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            old_value=old_value,
            new_value=new_value,
            extra_data=extra_data,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            user_email=user_email,
            user_role=user_role
        )
    
    @staticmethod
    def get_organization_logs(
        organization_id: int,
        limit: int = 50,
        offset: int = 0,
        action: Optional[str] = None,
        action_category: Optional[str] = None,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        severity: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene logs de auditoría con filtros opcionales
        
        Returns:
            Dict con logs y total de registros
        """
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
                # Agregar 23:59:59 para incluir todo el día
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
        
        # Búsqueda con filtros
        logs = AuditLog.search_logs(
            organization_id=organization_id,
            action=action,
            action_category=action_category,
            user_id=user_id,
            resource_type=resource_type,
            severity=severity,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=limit + offset  # Obtener más para aplicar offset
        )
        
        # Aplicar offset manualmente
        logs = logs[offset:offset + limit]
        
        # Contar total (para paginación)
        query = db.session.query(AuditLog).filter_by(organization_id=organization_id)
        
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
        if start_datetime:
            query = query.filter(AuditLog.created_at >= start_datetime)
        if end_datetime:
            query = query.filter(AuditLog.created_at <= end_datetime)
        
        total = query.count()
        
        return {
            'logs': [log.to_dict() for log in logs],
            'total': total,
            'limit': limit,
            'offset': offset
        }
    
    @staticmethod
    def get_organization_logs_paginated(
        organization_id: int,
        filters: Dict[str, Any],
        page: int = 1,
        per_page: int = 50
    ):
        """
        Obtiene logs de auditoría paginados con filtros
        
        Returns:
            Tuple[List[Dict], int]: (logs, total)
        """
        offset = (page - 1) * per_page
        
        # Convertir fechas si existen
        start_datetime = filters.get('start_date')
        end_datetime = filters.get('end_date')
        
        # Búsqueda con filtros
        logs = AuditLog.search_logs(
            organization_id=organization_id,
            action=filters.get('action'),
            action_category=filters.get('category'),
            user_id=filters.get('user_id'),
            resource_type=filters.get('resource_type'),
            severity=filters.get('severity'),
            start_date=start_datetime,
            end_date=end_datetime,
            limit=per_page + offset
        )
        
        # Aplicar offset y filtro de proyecto si existe
        proyecto_id = filters.get('proyecto_id')
        if proyecto_id:
            logs = [log for log in logs if log.resource_type == 'proyecto' and log.resource_id == proyecto_id]
        
        logs = logs[offset:offset + per_page]
        
        # Contar total
        query = db.session.query(AuditLog).filter_by(organization_id=organization_id)
        
        if filters.get('action'):
            query = query.filter_by(action=filters['action'])
        if filters.get('category'):
            query = query.filter_by(action_category=filters['category'])
        if filters.get('user_id'):
            query = query.filter_by(user_id=filters['user_id'])
        if filters.get('resource_type'):
            query = query.filter_by(resource_type=filters['resource_type'])
        if filters.get('severity'):
            query = query.filter_by(severity=filters['severity'])
        if start_datetime:
            query = query.filter(AuditLog.created_at >= start_datetime)
        if end_datetime:
            query = query.filter(AuditLog.created_at <= end_datetime)
        if proyecto_id:
            query = query.filter_by(resource_type='proyecto', resource_id=proyecto_id)
        
        total = query.count()
        
        return [log.to_dict() for log in logs], total
    
    @staticmethod
    def get_recent_activity(organization_id: int, user_id: Optional[int] = None, limit: int = 10):
        """Obtiene actividad reciente de la organización o usuario"""
        logs = AuditLog.get_recent_logs(
            organization_id=organization_id,
            limit=limit,
            user_id=user_id
        )
        
        return [log.to_dict(include_metadata=False) for log in logs]
    
    @staticmethod
    def get_user_activity(organization_id: int, user_id: int, days: int = 30):
        """Obtiene actividad de un usuario en los últimos N días"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        logs = AuditLog.search_logs(
            organization_id=organization_id,
            user_id=user_id,
            start_date=start_date,
            limit=200
        )
        
        return [log.to_dict() for log in logs]
    
    @staticmethod
    def get_resource_history(
        organization_id: int,
        resource_type: str,
        resource_id: int
    ) -> List[Dict]:
        """Obtiene el historial completo de un recurso"""
        logs = AuditLog.search_logs(
            organization_id=organization_id,
            resource_type=resource_type,
            limit=500
        )
        
        # Filtrar por resource_id específico
        resource_logs = [
            log for log in logs
            if log.resource_id == resource_id
        ]
        
        return [log.to_dict(include_metadata=True) for log in resource_logs]
    
    @staticmethod
    def get_audit_statistics(organization_id: int, days: int = 30) -> Dict[str, Any]:
        """Obtiene estadísticas de auditoría"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        logs = AuditLog.search_logs(
            organization_id=organization_id,
            start_date=start_date,
            limit=10000
        )
        
        # Contar por categoría
        by_category = {}
        by_severity = {}
        by_user = {}
        
        for log in logs:
            # Por categoría
            by_category[log.action_category] = by_category.get(log.action_category, 0) + 1
            
            # Por severidad
            by_severity[log.severity] = by_severity.get(log.severity, 0) + 1
            
            # Por usuario
            if log.user_email:
                by_user[log.user_email] = by_user.get(log.user_email, 0) + 1
        
        return {
            'total_actions': len(logs),
            'by_category': by_category,
            'by_severity': by_severity,
            'top_users': sorted(by_user.items(), key=lambda x: x[1], reverse=True)[:10],
            'period_days': days
        }
    
    @staticmethod
    def export_logs(
        organization_id: int,
        format: str = 'json',
        **filters
    ) -> Any:
        """
        Exporta logs en formato especificado
        
        Args:
            organization_id: ID de la organización
            format: Formato de exportación (json, csv)
            **filters: Filtros adicionales
            
        Returns:
            Datos en el formato solicitado
        """
        result = AuditService.get_organization_logs(
            organization_id=organization_id,
            limit=10000,  # Límite alto para exportación
            **filters
        )
        
        if format == 'json':
            return result['logs']
        
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            if result['logs']:
                fieldnames = ['created_at', 'user_email', 'action', 'action_category', 
                             'description', 'resource_type', 'resource_name', 'severity']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for log in result['logs']:
                    writer.writerow({
                        'created_at': log['created_at'],
                        'user_email': log.get('user_email', ''),
                        'action': log['action'],
                        'action_category': log['action_category'],
                        'description': log.get('description', ''),
                        'resource_type': log.get('resource_type', ''),
                        'resource_name': log.get('resource_name', ''),
                        'severity': log['severity']
                    })
            
            return output.getvalue()
        
        return result['logs']
