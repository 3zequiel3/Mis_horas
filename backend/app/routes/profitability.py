"""
Rutas API para Rentabilidad (Profitability)
Métricas financieras y reportes de rentabilidad
"""

from flask import Blueprint, request, jsonify
from app.decorators import requires_permission, organization_required, token_required, get_current_organization
from app.utils.response import success_response, error_response
from app.services.profitability_service import ProfitabilityService

profitability_bp = Blueprint('profitability', __name__, url_prefix='/api/profitability')

@profitability_bp.route('/project/<int:project_id>', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_project_profitability(project_id):
    """
    Obtiene la rentabilidad completa de un proyecto
    Incluye: horas, costos, ingresos, margen, health status
    """
    try:
        data = ProfitabilityService.calculate_project_profitability(project_id)
        return success_response(data=data)
    
    except ValueError as e:
        return error_response(str(e), 404)
    
    except Exception as e:
        return error_response(str(e), 500)

@profitability_bp.route('/organization', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_organization_profitability():
    """
    Obtiene rentabilidad total de la organización
    Suma todos los proyectos
    """
    try:
        org_id = get_current_organization()
        data = ProfitabilityService.calculate_organization_profitability(org_id)
        return success_response(data=data)
    
    except Exception as e:
        return error_response(str(e), 500)

@profitability_bp.route('/monthly/<int:year>/<int:month>', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_monthly_profitability(year, month):
    """
    Rentabilidad del mes especificado
    """
    try:
        org_id = get_current_organization()
        
        if month < 1 or month > 12:
            return error_response("Mes inválido (debe ser 1-12)", 400)
        
        data = ProfitabilityService.calculate_monthly_profitability(org_id, year, month)
        return success_response(data=data)
    
    except Exception as e:
        return error_response(str(e), 500)

@profitability_bp.route('/project/<int:project_id>/budget-health', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_budget_health(project_id):
    """
    Estado de salud del presupuesto del proyecto
    Burn rate, remaining, alertas
    """
    try:
        data = ProfitabilityService.get_budget_health(project_id)
        return success_response(data=data)
    
    except Exception as e:
        return error_response(str(e), 500)

@profitability_bp.route('/projects-at-risk', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_projects_at_risk():
    """
    Proyectos con burn rate alto (>85% por defecto)
    Query params:
        - threshold: default 85
    """
    try:
        org_id = get_current_organization()
        threshold = request.args.get('threshold', default=85.0, type=float)
        
        data = ProfitabilityService.get_projects_at_risk(org_id, threshold)
        return success_response(
            data=data,
            message=f"Se encontraron {len(data)} proyectos en riesgo"
        )
    
    except Exception as e:
        return error_response(str(e), 500)

@profitability_bp.route('/employee/<int:user_id>/cost', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def calculate_employee_cost(user_id):
    """
    Calcula el costo de un empleado en un proyecto
    Query params:
        - project_id: requerido
        - hours: requerido
    """
    try:
        project_id = request.args.get('project_id', type=int)
        hours = request.args.get('hours', type=float)
        
        if not project_id:
            return error_response("project_id es requerido", 400)
        
        if not hours:
            return error_response("hours es requerido", 400)
        
        data = ProfitabilityService.calculate_employee_cost(user_id, project_id, hours)
        return success_response(data=data)
    
    except ValueError as e:
        return error_response(str(e), 404)
    
    except Exception as e:
        return error_response(str(e), 500)

@profitability_bp.route('/project/<int:project_id>/expense-summary', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_expense_summary(project_id):
    """
    Resumen de gastos del proyecto por categoría
    """
    try:
        data = ProfitabilityService.get_expense_summary(project_id)
        return success_response(data=data)
    
    except Exception as e:
        return error_response(str(e), 500)

@profitability_bp.route('/dashboard', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_dashboard_metrics():
    """
    Métricas financieras para el dashboard
    Incluye: rentabilidad org, proyectos en riesgo, burn rate promedio
    """
    try:
        org_id = get_current_organization()
        
        # Rentabilidad general
        org_prof = ProfitabilityService.calculate_organization_profitability(org_id)
        
        # Proyectos en riesgo
        at_risk = ProfitabilityService.get_projects_at_risk(org_id, 85)
        
        return success_response(
            data={
                'organization': org_prof,
                'projects_at_risk': at_risk,
                'alerts': {
                    'high_burn_rate': len(at_risk),
                    'negative_margin': 1 if org_prof['profit_margin'] < 0 else 0
                }
            }
        )
    
    except Exception as e:
        return error_response(str(e), 500)
