"""
Rutas API para Project Budget Addons
Adicionales de presupuesto
Fase 4: UX Unificada & Gestión Financiera
"""

from flask import Blueprint, request
from app import db
from app.models.project_budget_addon import ProjectBudgetAddon
from app.models.proyecto import Proyecto
from app.decorators import requires_permission, organization_required, token_required, get_current_user, get_current_organization
from app.utils.response import success_response, error_response

budget_addons_bp = Blueprint('budget_addons', __name__, url_prefix='/api/projects')

@budget_addons_bp.route('/<int:project_id>/budget-addons', methods=['GET'])
@organization_required
@requires_permission('VIEW_PROJECT_DETAILS')
def get_project_addons(project_id):
    """
    Obtiene todos los adicionales de presupuesto de un proyecto
    """
    try:
        org_id = get_current_organization()
        
        # Verificar proyecto
        project = Proyecto.query.filter_by(id=project_id, organization_id=org_id).first()
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        addons = ProjectBudgetAddon.query.filter_by(
            project_id=project_id
        ).order_by(ProjectBudgetAddon.created_at.desc()).all()
        
        # Calcular total
        total_addons = ProjectBudgetAddon.get_project_total_addons(project_id)
        
        return success_response(
            data={
                'addons': [addon.to_dict() for addon in addons],
                'total_addons': total_addons,
                'budget_base': float(project.budget_base_amount) if project.budget_base_amount else 0,
                'total_budget': total_addons + (float(project.budget_base_amount) if project.budget_base_amount else 0),
                'currency': project.currency
            },
            message=f"Se encontraron {len(addons)} adicionales"
        )
    
    except Exception as e:
        return error_response(str(e), 500)

@budget_addons_bp.route('/<int:project_id>/budget-addons', methods=['POST'])
@organization_required
@requires_permission('MANAGE_PROJECT_SETTINGS')
def create_budget_addon(project_id):
    """
    Crea un nuevo adicional de presupuesto
    Body:
        {
            "name": "Fase 2 Extra",
            "description": "Funcionalidades adicionales",
            "amount": 5000.00
        }
    """
    try:
        org_id = get_current_organization()
        user = get_current_user()
        
        # Verificar proyecto
        project = Proyecto.query.filter_by(id=project_id, organization_id=org_id).first()
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        data = request.get_json()
        
        # Validaciones
        if 'name' not in data or 'amount' not in data:
            return error_response("Campos requeridos: name, amount", 400)
        
        addon = ProjectBudgetAddon(
            project_id=project_id,
            organization_id=org_id,
            name=data['name'],
            description=data.get('description'),
            amount=data['amount'],
            created_by=user['id']
        )
        
        db.session.add(addon)
        db.session.commit()
        
        # Calcular nuevo total
        total_budget = ProjectBudgetAddon.calculate_total_budget(
            project_id,
            float(project.budget_base_amount) if project.budget_base_amount else 0
        )
        
        return success_response(
            data={
                'addon': addon.to_dict(),
                'total_budget': total_budget
            },
            message="Adicional creado exitosamente",
            status_code=201
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@budget_addons_bp.route('/<int:project_id>/budget-addons/<int:addon_id>', methods=['PUT'])
@organization_required
@requires_permission('MANAGE_PROJECT_SETTINGS')
def update_budget_addon(project_id, addon_id):
    """Actualiza un adicional de presupuesto"""
    try:
        org_id = get_current_organization()
        
        addon = ProjectBudgetAddon.query.filter_by(
            id=addon_id,
            project_id=project_id,
            organization_id=org_id
        ).first()
        
        if not addon:
            return error_response("Adicional no encontrado", 404)
        
        data = request.get_json()
        
        if 'name' in data:
            addon.name = data['name']
        
        if 'description' in data:
            addon.description = data['description']
        
        if 'amount' in data:
            addon.amount = data['amount']
        
        db.session.commit()
        
        # Recalcular total
        project = Proyecto.query.get(project_id)
        total_budget = ProjectBudgetAddon.calculate_total_budget(
            project_id,
            float(project.budget_base_amount) if project.budget_base_amount else 0
        )
        
        return success_response(
            data={
                'addon': addon.to_dict(),
                'total_budget': total_budget
            },
            message="Adicional actualizado exitosamente"
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@budget_addons_bp.route('/<int:project_id>/budget-addons/<int:addon_id>', methods=['DELETE'])
@organization_required
@requires_permission('MANAGE_PROJECT_SETTINGS')
def delete_budget_addon(project_id, addon_id):
    """Elimina un adicional de presupuesto"""
    try:
        org_id = get_current_organization()
        
        addon = ProjectBudgetAddon.query.filter_by(
            id=addon_id,
            project_id=project_id,
            organization_id=org_id
        ).first()
        
        if not addon:
            return error_response("Adicional no encontrado", 404)
        
        db.session.delete(addon)
        db.session.commit()
        
        # Recalcular total
        project = Proyecto.query.get(project_id)
        total_budget = ProjectBudgetAddon.calculate_total_budget(
            project_id,
            float(project.budget_base_amount) if project.budget_base_amount else 0
        )
        
        return success_response(
            data={'total_budget': total_budget},
            message="Adicional eliminado exitosamente"
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@budget_addons_bp.route('/<int:project_id>/total-budget', methods=['GET'])
@organization_required
@requires_permission('VIEW_PROJECT_DETAILS')
def get_total_budget(project_id):
    """
    Obtiene el presupuesto total (base + adicionales)
    """
    try:
        org_id = get_current_organization()
        
        project = Proyecto.query.filter_by(id=project_id, organization_id=org_id).first()
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        base_amount = float(project.budget_base_amount) if project.budget_base_amount else 0
        total_budget = ProjectBudgetAddon.calculate_total_budget(project_id, base_amount)
        addons_total = ProjectBudgetAddon.get_project_total_addons(project_id)
        
        return success_response(
            data={
                'budget_type': project.budget_type,
                'budget_base': base_amount,
                'addons_total': addons_total,
                'total_budget': total_budget,
                'currency': project.currency
            }
        )
    
    except Exception as e:
        return error_response(str(e), 500)
