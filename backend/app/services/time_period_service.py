"""
Servicio de Gestión de Períodos de Tiempo
Sistema de aprobación de hojas de tiempo
"""

from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, date
from app.models import TimePeriod, TimePeriodStatus, Dia, Empleado, Proyecto
from app.services.audit_service import AuditService
from app.models import AuditAction, AuditCategory
from app import db


class TimePeriodService:
    """Servicio para gestión de períodos de tiempo y aprobaciones"""
    
    @staticmethod
    def get_or_create_period(
        organization_id: int,
        proyecto_id: int,
        empleado_id: int,
        anio: int,
        mes: int
    ) -> TimePeriod:
        """Obtiene o crea un período de tiempo"""
        return TimePeriod.get_or_create_period(
            organization_id=organization_id,
            proyecto_id=proyecto_id,
            empleado_id=empleado_id,
            anio=anio,
            mes=mes
        )
    
    @staticmethod
    def get_employee_periods(
        organization_id: int,
        empleado_id: int,
        anio: Optional[int] = None,
        mes: Optional[int] = None
    ) -> List[Dict]:
        """Obtiene períodos de un empleado"""
        periods = TimePeriod.get_employee_periods(
            organization_id=organization_id,
            empleado_id=empleado_id,
            anio=anio,
            mes=mes
        )
        
        return [p.to_dict(include_details=True) for p in periods]
    
    @staticmethod
    def get_project_periods(
        organization_id: int,
        proyecto_id: int,
        anio: Optional[int] = None,
        mes: Optional[int] = None
    ) -> List[Dict]:
        """Obtiene todos los períodos de un proyecto"""
        query = TimePeriod.query.filter_by(
            organization_id=organization_id,
            proyecto_id=proyecto_id
        )
        
        if anio:
            query = query.filter_by(anio=anio)
        if mes:
            query = query.filter_by(mes=mes)
        
        periods = query.order_by(TimePeriod.anio.desc(), TimePeriod.mes.desc()).all()
        
        result = []
        for period in periods:
            period_dict = period.to_dict(include_details=True)
            
            # Agregar información del empleado
            empleado = Empleado.query.get(period.empleado_id)
            if empleado:
                period_dict['empleado_nombre'] = empleado.nombre
                result.append(period_dict)
        
        return result
    
    @staticmethod
    def get_pending_approvals(organization_id: int, proyecto_id: Optional[int] = None) -> List[Dict]:
        """Obtiene períodos pendientes de aprobación"""
        periods = TimePeriod.get_pending_for_review(organization_id)
        
        result = []
        for period in periods:
            # Filtrar por proyecto si se especifica
            if proyecto_id and period.proyecto_id != proyecto_id:
                continue
                
            period_dict = period.to_dict(include_details=True)
            
            # Agregar información del empleado y proyecto
            empleado = Empleado.query.get(period.empleado_id)
            proyecto = Proyecto.query.get(period.proyecto_id)
            
            if empleado and proyecto:
                period_dict['empleado_nombre'] = empleado.nombre
                period_dict['proyecto_nombre'] = proyecto.nombre
                
                result.append(period_dict)
        
        return result
    
    @staticmethod
    def submit_period_for_approval(
        organization_id: int,
        period_id: int,
        user_id: int,
        user_email: str,
        user_role: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Envía un período para aprobación
        
        Returns:
            Tuple[success, error_message]
        """
        period = TimePeriod.query.filter_by(
            id=period_id,
            organization_id=organization_id
        ).first()
        
        if not period:
            return False, "Período no encontrado"
        
        if not period.can_submit():
            return False, f"El período no puede ser enviado. Estado actual: {period.status}"
        
        # Calcular totales antes de enviar
        TimePeriodService._update_period_totals(period)
        
        # Cambiar estado de todos los días del período
        dias = Dia.query.filter_by(
            proyecto_id=period.proyecto_id,
            empleado_id=period.empleado_id
        ).filter(
            db.extract('year', Dia.fecha) == period.anio,
            db.extract('month', Dia.fecha) == period.mes
        ).all()
        
        for dia in dias:
            dia.status = TimePeriodStatus.PENDING
            dia.time_period_id = period.id
        
        # Enviar período
        success = period.submit_for_approval(user_id)
        
        if success:
            db.session.commit()
            
            # Log de auditoría
            AuditService.log_action(
                organization_id=organization_id,
                user_id=user_id,
                action=AuditAction.SUBMIT_TIMESHEET,
                action_category=AuditCategory.TIME,
                description=f"Período {period.anio}/{period.mes} enviado para aprobación",
                resource_type='time_period',
                resource_id=period.id,
                resource_name=f"Período {period.anio}-{period.mes:02d}",
                extra_data={
                    'total_hours': period.total_hours,
                    'total_days': period.total_days
                },
                severity='info',
                user_email=user_email,
                user_role=user_role
            )
            
            return True, None
        
        return False, "No se pudo enviar el período"
    
    @staticmethod
    def approve_period(
        organization_id: int,
        period_id: int,
        reviewer_id: int,
        reviewer_email: str,
        reviewer_role: str,
        notes: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Aprueba un período de tiempo
        
        Returns:
            Tuple[success, error_message]
        """
        period = TimePeriod.query.filter_by(
            id=period_id,
            organization_id=organization_id
        ).first()
        
        if not period:
            return False, "Período no encontrado"
        
        if not period.can_approve():
            return False, f"El período no puede ser aprobado. Estado actual: {period.status}"
        
        # Aprobar período
        success = period.approve(reviewer_id, notes)
        
        if success:
            # Cambiar estado de todos los días asociados
            dias = Dia.query.filter_by(time_period_id=period.id).all()
            for dia in dias:
                dia.status = TimePeriodStatus.APPROVED
            
            db.session.commit()
            
            # Log de auditoría
            AuditService.log_action(
                organization_id=organization_id,
                user_id=reviewer_id,
                action=AuditAction.APPROVE_TIMESHEET,
                action_category=AuditCategory.TIME,
                description=f"Período {period.anio}/{period.mes} aprobado",
                resource_type='time_period',
                resource_id=period.id,
                resource_name=f"Período {period.anio}-{period.mes:02d}",
                extra_data={
                    'total_hours': period.total_hours,
                    'notes': notes
                },
                severity='info',
                user_email=reviewer_email,
                user_role=reviewer_role
            )
            
            return True, None
        
        return False, "No se pudo aprobar el período"
    
    @staticmethod
    def reject_period(
        organization_id: int,
        period_id: int,
        reviewer_id: int,
        reviewer_email: str,
        reviewer_role: str,
        notes: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Rechaza un período de tiempo con notas explicativas
        
        Returns:
            Tuple[success, error_message]
        """
        if not notes or len(notes.strip()) < 10:
            return False, "Las notas de rechazo son obligatorias (mínimo 10 caracteres)"
        
        period = TimePeriod.query.filter_by(
            id=period_id,
            organization_id=organization_id
        ).first()
        
        if not period:
            return False, "Período no encontrado"
        
        if not period.can_approve():
            return False, f"El período no puede ser rechazado. Estado actual: {period.status}"
        
        # Rechazar período
        success = period.reject(reviewer_id, notes)
        
        if success:
            # Cambiar estado de todos los días asociados
            dias = Dia.query.filter_by(time_period_id=period.id).all()
            for dia in dias:
                dia.status = TimePeriodStatus.REJECTED
            
            db.session.commit()
            
            # Log de auditoría
            AuditService.log_action(
                organization_id=organization_id,
                user_id=reviewer_id,
                action=AuditAction.REJECT_TIMESHEET,
                action_category=AuditCategory.TIME,
                description=f"Período {period.anio}/{period.mes} rechazado",
                resource_type='time_period',
                resource_id=period.id,
                resource_name=f"Período {period.anio}-{period.mes:02d}",
                extra_data={
                    'total_hours': period.total_hours,
                    'notes': notes
                },
                severity='warning',
                user_email=reviewer_email,
                user_role=reviewer_role
            )
            
            return True, None
        
        return False, "No se pudo rechazar el período"
    
    @staticmethod
    def reopen_period(
        organization_id: int,
        period_id: int,
        user_id: int,
        user_email: str,
        user_role: str,
        reason: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Reabre un período aprobado o bloqueado
        Solo Owner y Admin pueden hacer esto
        
        Returns:
            Tuple[success, error_message]
        """
        if not reason or len(reason.strip()) < 10:
            return False, "La razón de reapertura es obligatoria (mínimo 10 caracteres)"
        
        period = TimePeriod.query.filter_by(
            id=period_id,
            organization_id=organization_id
        ).first()
        
        if not period:
            return False, "Período no encontrado"
        
        if not period.can_reopen():
            return False, f"El período no puede ser reabierto. Estado actual: {period.status}"
        
        old_status = period.status
        
        # Reabrir período
        success = period.reopen(user_id, reason)
        
        if success:
            # Cambiar estado de todos los días asociados
            dias = Dia.query.filter_by(time_period_id=period.id).all()
            for dia in dias:
                dia.status = TimePeriodStatus.DRAFT
            
            db.session.commit()
            
            # Log de auditoría crítico
            AuditService.log_action(
                organization_id=organization_id,
                user_id=user_id,
                action=AuditAction.REOPEN_TIMESHEET,
                action_category=AuditCategory.TIME,
                description=f"Período {period.anio}/{period.mes} reabierto",
                resource_type='time_period',
                resource_id=period.id,
                resource_name=f"Período {period.anio}-{period.mes:02d}",
                old_value={'status': old_status},
                new_value={'status': period.status},
                extra_data={
                    'reason': reason,
                    'total_hours': period.total_hours
                },
                severity='critical',
                user_email=user_email,
                user_role=user_role
            )
            
            return True, None
        
        return False, "No se pudo reabrir el período"
    
    @staticmethod
    def lock_period(
        organization_id: int,
        period_id: int,
        user_id: int,
        user_email: str,
        user_role: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Bloquea permanentemente un período aprobado
        
        Returns:
            Tuple[success, error_message]
        """
        period = TimePeriod.query.filter_by(
            id=period_id,
            organization_id=organization_id
        ).first()
        
        if not period:
            return False, "Período no encontrado"
        
        if period.status != TimePeriodStatus.APPROVED:
            return False, "Solo se pueden bloquear períodos aprobados"
        
        # Bloquear período
        success = period.lock()
        
        if success:
            # Cambiar estado de todos los días asociados
            dias = Dia.query.filter_by(time_period_id=period.id).all()
            for dia in dias:
                dia.status = TimePeriodStatus.LOCKED
            
            db.session.commit()
            
            # Log de auditoría
            AuditService.log_action(
                organization_id=organization_id,
                user_id=user_id,
                action=AuditAction.LOCK_PERIOD,
                action_category=AuditCategory.TIME,
                description=f"Período {period.anio}/{period.mes} bloqueado permanentemente",
                resource_type='time_period',
                resource_id=period.id,
                resource_name=f"Período {period.anio}-{period.mes:02d}",
                severity='warning',
                user_email=user_email,
                user_role=user_role
            )
            
            return True, None
        
        return False, "No se pudo bloquear el período"
    
    @staticmethod
    def _update_period_totals(period: TimePeriod):
        """Actualiza los totales de un período"""
        dias = Dia.query.filter_by(
            proyecto_id=period.proyecto_id,
            empleado_id=period.empleado_id
        ).filter(
            db.extract('year', Dia.fecha) == period.anio,
            db.extract('month', Dia.fecha) == period.mes
        ).all()
        
        total_hours = sum(dia.horas_trabajadas or 0 for dia in dias)
        total_days = len([dia for dia in dias if (dia.horas_trabajadas or 0) > 0])
        
        period.update_totals(total_hours, total_days)
    
    @staticmethod
    def get_period_details(organization_id: int, period_id: int) -> Optional[Dict]:
        """Obtiene detalles completos de un período incluyendo días"""
        period = TimePeriod.query.filter_by(
            id=period_id,
            organization_id=organization_id
        ).first()
        
        if not period:
            return None
        
        # Obtener días del período
        dias = Dia.query.filter_by(
            proyecto_id=period.proyecto_id,
            empleado_id=period.empleado_id
        ).filter(
            db.extract('year', Dia.fecha) == period.anio,
            db.extract('month', Dia.fecha) == period.mes
        ).order_by(Dia.fecha).all()
        
        # Información del empleado y proyecto
        empleado = Empleado.query.get(period.empleado_id)
        proyecto = Proyecto.query.get(period.proyecto_id)
        
        period_dict = period.to_dict(include_details=True)
        period_dict['dias'] = [dia.to_dict() for dia in dias]
        period_dict['empleado'] = empleado.to_dict() if empleado else None
        period_dict['proyecto'] = {'id': proyecto.id, 'nombre': proyecto.nombre} if proyecto else None
        
        return period_dict
