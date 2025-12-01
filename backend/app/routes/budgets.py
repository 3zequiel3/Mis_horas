"""
Rutas API para Presupuestos (Budgets)
Gestión de presupuestos y tracking de consumo
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.budget import Budget, BudgetType
from app.models.proyecto import Proyecto
from app.decorators import requires_permission, organization_required, token_required, get_current_user, get_current_organization
from app.utils.response import success_response, error_response
from app.services.profitability_service import ProfitabilityService
from sqlalchemy.exc import IntegrityError

budgets_bp = Blueprint('budgets', __name__, url_prefix='/api/budgets')

@budgets_bp.route('/project/<int:project_id>', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_project_budget(project_id):
    """Obtiene el presupuesto de un proyecto"""
    try:
        org_id = get_current_organization()
        
        # Verificar proyecto
        project = Proyecto.query.filter_by(id=project_id, organization_id=org_id).first()
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        budget = Budget.query.filter_by(project_id=project_id).first()
        
        if not budget:
            return error_response("Proyecto sin presupuesto configurado", 404)
        
        # Incluir datos de salud
        health = ProfitabilityService.get_budget_health(project_id)
        
        return success_response(
            data={
                **budget.to_dict(),
                'health': health
            }
        )
    
    except Exception as e:
        return error_response(str(e), 500)

@budgets_bp.route('', methods=['POST'])
@organization_required
@requires_permission('MANAGE_FINANCIAL_DATA')
def create_budget():
    """
    Crea un nuevo presupuesto
    Body:
        {
            "project_id": 1,
            "budget_type": "none|monetary|hours|fixed",
            "total_amount": 10000.00 (requerido si budget_type=monetary o fixed),
            "total_hours": 200 (requerido si budget_type=hours),
            "alert_threshold_percentage": 80,
            "notes": "..."
        }
    """
    try:
        org_id = get_current_organization()
        user = get_current_user()
        data = request.get_json()
        
        # Validaciones
        if 'project_id' not in data:
            return error_response("project_id es requerido", 400)
        
        if 'budget_type' not in data:
            return error_response("budget_type es requerido", 400)
        
        # Verificar proyecto
        project = Proyecto.query.filter_by(
            id=data['project_id'],
            organization_id=org_id
        ).first()
        
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        # Verificar que no exista presupuesto
        existing = Budget.query.filter_by(project_id=data['project_id']).first()
        if existing:
            return error_response("El proyecto ya tiene un presupuesto", 409)
        
        budget_type = BudgetType(data['budget_type'])
        
        # Validar campos según tipo
        if budget_type in [BudgetType.MONETARY, BudgetType.FIXED_PRICE]:
            if 'total_amount' not in data:
                return error_response("total_amount es requerido para este tipo de presupuesto", 400)
        
        if budget_type == BudgetType.HOURS:
            if 'total_hours' not in data:
                return error_response("total_hours es requerido para budget_type=hours", 400)
        
        # Crear presupuesto
        budget = Budget(
            organization_id=org_id,
            project_id=data['project_id'],
            budget_type=budget_type,
            total_amount=data.get('total_amount'),
            total_hours=data.get('total_hours'),
            alert_threshold_percentage=data.get('alert_threshold_percentage', 80),
            notes=data.get('notes'),
            created_by=user['id']
        )
        
        db.session.add(budget)
        db.session.commit()
        
        return success_response(
            data=budget.to_dict(),
            message="Presupuesto creado exitosamente",
            status_code=201
        )
    
    except IntegrityError:
        db.session.rollback()
        return error_response("Error de integridad en la base de datos", 409)
    
    except ValueError as e:
        return error_response(str(e), 400)
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@budgets_bp.route('/<int:budget_id>', methods=['PUT'])
@organization_required
@requires_permission('MANAGE_FINANCIAL_DATA')
def update_budget(budget_id):
    """Actualiza un presupuesto"""
    try:
        org_id = get_current_organization()
        budget = Budget.query.filter_by(id=budget_id, organization_id=org_id).first()
        
        if not budget:
            return error_response("Presupuesto no encontrado", 404)
        
        if budget.is_locked:
            return error_response("El presupuesto está bloqueado", 403)
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'total_amount' in data and budget.budget_type in [BudgetType.MONETARY, BudgetType.FIXED_PRICE]:
            budget.total_amount = data['total_amount']
            # Recalcular is_exceeded
            budget.recalculate_exceeded()
        
        if 'total_hours' in data and budget.budget_type == BudgetType.HOURS:
            budget.total_hours = data['total_hours']
            budget.recalculate_exceeded()
        
        if 'alert_threshold_percentage' in data:
            budget.alert_threshold_percentage = data['alert_threshold_percentage']
        
        if 'notes' in data:
            budget.notes = data['notes']
        
        db.session.commit()
        
        return success_response(
            data=budget.to_dict(),
            message="Presupuesto actualizado exitosamente"
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@budgets_bp.route('/<int:budget_id>/consumption', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_budget_consumption(budget_id):
    """
    Obtiene detalles del consumo del presupuesto
    Incluye burn rate, remaining, health status
    """
    try:
        org_id = get_current_organization()
        budget = Budget.query.filter_by(id=budget_id, organization_id=org_id).first()
        
        if not budget:
            return error_response("Presupuesto no encontrado", 404)
        
        burn_rate = budget.calculate_burn_rate()
        remaining = budget.calculate_remaining()
        health = budget.get_health_status()
        
        return success_response(
            data={
                'budget_id': budget.id,
                'project_id': budget.project_id,
                'budget_type': budget.budget_type.value,
                'total_amount': float(budget.total_amount) if budget.total_amount else None,
                'total_hours': float(budget.total_hours) if budget.total_hours else None,
                'consumed_amount': float(budget.consumed_amount),
                'consumed_hours': float(budget.consumed_hours),
                'additional_expenses': float(budget.additional_expenses),
                'burn_rate_percentage': round(burn_rate, 2),
                'remaining': remaining,
                'health_status': health,
                'is_exceeded': budget.is_exceeded,
                'should_alert': budget.should_send_alert(),
                'alert_threshold': budget.alert_threshold_percentage
            }
        )
    
    except Exception as e:
        return error_response(str(e), 500)

@budgets_bp.route('/<int:budget_id>/reset', methods=['POST'])
@organization_required
@requires_permission('MANAGE_FINANCIAL_DATA')
def reset_budget(budget_id):
    """
    Reinicia el presupuesto (para nuevo período)
    Body:
        {
            "new_total_amount": 10000.00 (opcional),
            "new_total_hours": 200 (opcional)
        }
    """
    try:
        org_id = get_current_organization()
        budget = Budget.query.filter_by(id=budget_id, organization_id=org_id).first()
        
        if not budget:
            return error_response("Presupuesto no encontrado", 404)
        
        data = request.get_json() or {}
        
        # Actualizar totales si se proporcionan
        if 'new_total_amount' in data:
            budget.total_amount = data['new_total_amount']
        
        if 'new_total_hours' in data:
            budget.total_hours = data['new_total_hours']
        
        # Reiniciar consumo
        budget.consumed_amount = 0
        budget.consumed_hours = 0
        budget.additional_expenses = 0
        budget.is_exceeded = False
        budget.is_locked = False
        
        db.session.commit()
        
        return success_response(
            data=budget.to_dict(),
            message="Presupuesto reiniciado exitosamente"
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@budgets_bp.route('/<int:budget_id>/lock', methods=['POST'])
@organization_required
@requires_permission('MANAGE_FINANCIAL_DATA')
def lock_budget(budget_id):
    """Bloquea el presupuesto (no se puede modificar)"""
    try:
        org_id = get_current_organization()
        budget = Budget.query.filter_by(id=budget_id, organization_id=org_id).first()
        
        if not budget:
            return error_response("Presupuesto no encontrado", 404)
        
        budget.is_locked = True
        db.session.commit()
        
        return success_response(
            data=budget.to_dict(),
            message="Presupuesto bloqueado exitosamente"
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@budgets_bp.route('/<int:budget_id>/unlock', methods=['POST'])
@organization_required
@requires_permission('MANAGE_FINANCIAL_DATA')
def unlock_budget(budget_id):
    """Desbloquea el presupuesto"""
    try:
        org_id = get_current_organization()
        budget = Budget.query.filter_by(id=budget_id, organization_id=org_id).first()
        
        if not budget:
            return error_response("Presupuesto no encontrado", 404)
        
        budget.is_locked = False
        db.session.commit()
        
        return success_response(
            data=budget.to_dict(),
            message="Presupuesto desbloqueado exitosamente"
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@budgets_bp.route('/organization/at-risk', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_at_risk_projects():
    """
    Obtiene proyectos con burn rate alto
    Query params:
        - threshold: default 85
    """
    try:
        org_id = get_current_organization()
        threshold = request.args.get('threshold', default=85.0, type=float)
        
        at_risk = ProfitabilityService.get_projects_at_risk(org_id, threshold)
        
        return success_response(
            data=at_risk,
            message=f"Se encontraron {len(at_risk)} proyectos en riesgo"
        )
    
    except Exception as e:
        return error_response(str(e), 500)

@budgets_bp.route('/organization/summary', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_organization_budget_summary():
    """Resumen de presupuestos de todos los proyectos"""
    try:
        org_id = get_current_organization()
        
        budgets = Budget.query.join(Proyecto).filter(
            Proyecto.organization_id == org_id
        ).all()
        
        summary = {
            'total_projects_with_budget': len(budgets),
            'total_budgeted_amount': 0,
            'total_consumed_amount': 0,
            'total_budgeted_hours': 0,
            'total_consumed_hours': 0,
            'projects_by_health': {
                'healthy': 0,
                'warning': 0,
                'critical': 0,
                'exceeded': 0
            }
        }
        
        for budget in budgets:
            if budget.total_amount:
                summary['total_budgeted_amount'] += float(budget.total_amount)
            
            summary['total_consumed_amount'] += float(budget.consumed_amount)
            
            if budget.total_hours:
                summary['total_budgeted_hours'] += float(budget.total_hours)
            
            summary['total_consumed_hours'] += float(budget.consumed_hours)
            
            health = budget.get_health_status()
            summary['projects_by_health'][health] += 1
        
        return success_response(data=summary)
    
    except Exception as e:
        return error_response(str(e), 500)
