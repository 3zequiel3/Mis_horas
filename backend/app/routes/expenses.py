"""
Rutas API para Gastos (Project Expenses)
Gestión de gastos no humanos del proyecto
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models.project_expense import ProjectExpense, ExpenseCategory
from app.models.proyecto import Proyecto
from app.decorators import requires_permission, organization_required, token_required, get_current_user, get_current_organization
from app.utils.response import success_response, error_response
from app.services.profitability_service import ProfitabilityService

expenses_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')

@expenses_bp.route('/project/<int:project_id>', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_project_expenses(project_id):
    """
    Obtiene todos los gastos de un proyecto
    Query params:
        - is_approved: filtrar por estado de aprobación
        - is_billable: filtrar por facturables
        - category: filtrar por categoría
    """
    try:
        org_id = get_current_organization()
        
        # Verificar proyecto
        project = Proyecto.query.filter_by(id=project_id, organization_id=org_id).first()
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        query = ProjectExpense.query.filter_by(project_id=project_id)
        
        # Filtros
        is_approved = request.args.get('is_approved')
        if is_approved is not None:
            query = query.filter_by(is_approved=is_approved.lower() == 'true')
        
        is_billable = request.args.get('is_billable')
        if is_billable is not None:
            query = query.filter_by(is_billable=is_billable.lower() == 'true')
        
        category = request.args.get('category')
        if category:
            query = query.filter_by(category=ExpenseCategory(category))
        
        expenses = query.order_by(ProjectExpense.expense_date.desc()).all()
        
        return success_response(
            data=[expense.to_dict() for expense in expenses],
            message=f"Se encontraron {len(expenses)} gastos"
        )
    
    except Exception as e:
        return error_response(str(e), 500)

@expenses_bp.route('/<int:expense_id>', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_expense(expense_id):
    """Obtiene un gasto específico"""
    try:
        org_id = get_current_organization()
        expense = ProjectExpense.query.filter_by(id=expense_id, organization_id=org_id).first()
        
        if not expense:
            return error_response("Gasto no encontrado", 404)
        
        return success_response(data=expense.to_dict())
    
    except Exception as e:
        return error_response(str(e), 500)

@expenses_bp.route('', methods=['POST'])
@organization_required
@requires_permission('MANAGE_EXPENSES')
def create_expense():
    """
    Crea un nuevo gasto
    Body:
        {
            "project_id": 1,
            "category": "software|hardware|services|travel|materials|subcontractors|other",
            "description": "Licencia AWS",
            "amount": 150.00,
            "expense_date": "2024-01-15",
            "is_recurring": false,
            "recurrence_frequency": "monthly" (opcional),
            "receipt_url": "https://...",
            "vendor": "Amazon Web Services",
            "is_billable": true,
            "notes": "..."
        }
    """
    try:
        org_id = get_current_organization()
        user = get_current_user()
        data = request.get_json()
        
        # Validaciones
        required_fields = ['project_id', 'category', 'description', 'amount', 'expense_date']
        for field in required_fields:
            if field not in data:
                return error_response(f"Campo requerido: {field}", 400)
        
        # Verificar proyecto
        project = Proyecto.query.filter_by(
            id=data['project_id'],
            organization_id=org_id
        ).first()
        
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        # Parsear fecha
        try:
            expense_date = datetime.strptime(data['expense_date'], '%Y-%m-%d').date()
        except ValueError:
            return error_response("Formato de fecha inválido (usar YYYY-MM-DD)", 400)
        
        # Crear gasto
        expense = ProjectExpense(
            organization_id=org_id,
            project_id=data['project_id'],
            category=ExpenseCategory(data['category']),
            description=data['description'],
            amount=data['amount'],
            expense_date=expense_date,
            is_recurring=data.get('is_recurring', False),
            recurrence_frequency=data.get('recurrence_frequency'),
            receipt_url=data.get('receipt_url'),
            vendor=data.get('vendor'),
            is_billable=data.get('is_billable', True),
            notes=data.get('notes'),
            created_by=user['id']
        )
        
        db.session.add(expense)
        db.session.commit()
        
        return success_response(
            data=expense.to_dict(),
            message="Gasto creado exitosamente",
            status_code=201
        )
    
    except ValueError as e:
        return error_response(str(e), 400)
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@expenses_bp.route('/<int:expense_id>', methods=['PUT'])
@organization_required
@requires_permission('MANAGE_EXPENSES')
def update_expense(expense_id):
    """Actualiza un gasto (solo si no está aprobado)"""
    try:
        org_id = get_current_organization()
        expense = ProjectExpense.query.filter_by(id=expense_id, organization_id=org_id).first()
        
        if not expense:
            return error_response("Gasto no encontrado", 404)
        
        if expense.is_approved:
            return error_response("No se puede modificar un gasto aprobado", 403)
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'description' in data:
            expense.description = data['description']
        
        if 'amount' in data:
            expense.amount = data['amount']
        
        if 'expense_date' in data:
            expense.expense_date = datetime.strptime(data['expense_date'], '%Y-%m-%d').date()
        
        if 'category' in data:
            expense.category = ExpenseCategory(data['category'])
        
        if 'is_recurring' in data:
            expense.is_recurring = data['is_recurring']
        
        if 'recurrence_frequency' in data:
            expense.recurrence_frequency = data['recurrence_frequency']
        
        if 'receipt_url' in data:
            expense.receipt_url = data['receipt_url']
        
        if 'vendor' in data:
            expense.vendor = data['vendor']
        
        if 'is_billable' in data:
            expense.is_billable = data['is_billable']
        
        if 'notes' in data:
            expense.notes = data['notes']
        
        db.session.commit()
        
        return success_response(
            data=expense.to_dict(),
            message="Gasto actualizado exitosamente"
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@expenses_bp.route('/<int:expense_id>/approve', methods=['POST'])
@organization_required
@requires_permission('APPROVE_EXPENSES')
def approve_expense(expense_id):
    """
    Aprueba un gasto (solo administradores)
    Actualiza el presupuesto automáticamente
    """
    try:
        org_id = get_current_organization()
        user = get_current_user()
        expense = ProjectExpense.query.filter_by(id=expense_id, organization_id=org_id).first()
        
        if not expense:
            return error_response("Gasto no encontrado", 404)
        
        if expense.is_approved:
            return error_response("El gasto ya está aprobado", 400)
        
        # Aprobar gasto (actualiza presupuesto automáticamente)
        expense.approve(user['id'])
        db.session.commit()
        
        return success_response(
            data=expense.to_dict(),
            message="Gasto aprobado exitosamente"
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@expenses_bp.route('/<int:expense_id>/reject', methods=['POST'])
@organization_required
@requires_permission('APPROVE_EXPENSES')
def reject_expense(expense_id):
    """Rechaza un gasto pendiente"""
    try:
        org_id = get_current_organization()
        expense = ProjectExpense.query.filter_by(id=expense_id, organization_id=org_id).first()
        
        if not expense:
            return error_response("Gasto no encontrado", 404)
        
        if expense.is_approved:
            return error_response("No se puede rechazar un gasto aprobado", 400)
        
        # Simplemente eliminar el gasto
        db.session.delete(expense)
        db.session.commit()
        
        return success_response(message="Gasto rechazado y eliminado")
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@expenses_bp.route('/<int:expense_id>', methods=['DELETE'])
@organization_required
@requires_permission('MANAGE_EXPENSES')
def delete_expense(expense_id):
    """Elimina un gasto (solo si no está aprobado)"""
    try:
        org_id = get_current_organization()
        expense = ProjectExpense.query.filter_by(id=expense_id, organization_id=org_id).first()
        
        if not expense:
            return error_response("Gasto no encontrado", 404)
        
        if expense.is_approved:
            return error_response("No se puede eliminar un gasto aprobado", 403)
        
        db.session.delete(expense)
        db.session.commit()
        
        return success_response(message="Gasto eliminado exitosamente")
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@expenses_bp.route('/project/<int:project_id>/total', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_project_total(project_id):
    """
    Obtiene el total de gastos del proyecto
    Solo incluye gastos aprobados
    """
    try:
        org_id = get_current_organization()
        
        # Verificar proyecto
        project = Proyecto.query.filter_by(id=project_id, organization_id=org_id).first()
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        total = ProjectExpense.get_project_total(project_id)
        billable_total = ProjectExpense.get_billable_total(project_id)
        
        return success_response(
            data={
                'project_id': project_id,
                'total_expenses': round(total, 2),
                'billable_expenses': round(billable_total, 2),
                'non_billable_expenses': round(total - billable_total, 2)
            }
        )
    
    except Exception as e:
        return error_response(str(e), 500)

@expenses_bp.route('/project/<int:project_id>/summary', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_expense_summary(project_id):
    """
    Resumen detallado de gastos por categoría
    """
    try:
        org_id = get_current_organization()
        
        # Verificar proyecto
        project = Proyecto.query.filter_by(id=project_id, organization_id=org_id).first()
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        summary = ProfitabilityService.get_expense_summary(project_id)
        
        return success_response(data=summary)
    
    except Exception as e:
        return error_response(str(e), 500)

@expenses_bp.route('/project/<int:project_id>/pending', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_pending_expenses(project_id):
    """Obtiene gastos pendientes de aprobación"""
    try:
        org_id = get_current_organization()
        
        # Verificar proyecto
        project = Proyecto.query.filter_by(id=project_id, organization_id=org_id).first()
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        pending = ProjectExpense.query.filter_by(
            project_id=project_id,
            is_approved=False
        ).order_by(ProjectExpense.created_at.asc()).all()
        
        return success_response(
            data=[expense.to_dict() for expense in pending],
            message=f"Se encontraron {len(pending)} gastos pendientes"
        )
    
    except Exception as e:
        return error_response(str(e), 500)
