"""
Rutas API para Tarifas (Rates)
Gestión de tarifas internas y de facturación
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.rate import Rate, RateType
from app.models.proyecto import Proyecto
from app.decorators import requires_permission, organization_required, token_required, get_current_user, get_current_organization
from app.utils.response import success_response, error_response
from sqlalchemy.exc import IntegrityError

rates_bp = Blueprint('rates', __name__, url_prefix='/api/rates')

@rates_bp.route('', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_rates():
    """
    Obtiene todas las tarifas de la organización
    Query params:
        - rate_type: filtrar por tipo
        - project_id: filtrar por proyecto
        - is_active: filtrar por estado
    """
    try:
        org_id = get_current_organization()
        
        query = Rate.query.filter_by(organization_id=org_id)
        
        # Filtros
        rate_type = request.args.get('rate_type')
        if rate_type:
            query = query.filter_by(rate_type=RateType(rate_type))
        
        project_id = request.args.get('project_id')
        if project_id:
            query = query.filter_by(project_id=int(project_id))
        
        is_active = request.args.get('is_active')
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        rates = query.order_by(Rate.created_at.desc()).all()
        
        return success_response(
            data=[rate.to_dict() for rate in rates],
            message=f"Se encontraron {len(rates)} tarifas"
        )
    
    except Exception as e:
        return error_response(str(e), 500)

@rates_bp.route('/<int:rate_id>', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_rate(rate_id):
    """Obtiene una tarifa específica"""
    try:
        org_id = get_current_organization()
        rate = Rate.query.filter_by(id=rate_id, organization_id=org_id).first()
        
        if not rate:
            return error_response("Tarifa no encontrada", 404)
        
        return success_response(data=rate.to_dict())
    
    except Exception as e:
        return error_response(str(e), 500)

@rates_bp.route('', methods=['POST'])
@organization_required
@requires_permission('MANAGE_FINANCIAL_DATA')
def create_rate():
    """
    Crea una nueva tarifa
    Body:
        {
            "rate_type": "project|person|task|role",
            "internal_cost": 15.00,
            "billing_rate": 50.00,
            "project_id": 1 (opcional, requerido si rate_type=project),
            "user_id": 1 (opcional, requerido si rate_type=person),
            "task_type": "desarrollo" (opcional, requerido si rate_type=task),
            "role": "senior" (opcional, requerido si rate_type=role),
            "currency": "USD",
            "notes": "..."
        }
    """
    try:
        org_id = get_current_organization()
        user = get_current_user()
        data = request.get_json()
        
        # Validaciones
        required_fields = ['rate_type', 'internal_cost', 'billing_rate']
        for field in required_fields:
            if field not in data:
                return error_response(f"Campo requerido: {field}", 400)
        
        rate_type = RateType(data['rate_type'])
        
        # Validar campos según tipo
        if rate_type == RateType.PROJECT and 'project_id' not in data:
            return error_response("project_id es requerido para rate_type=project", 400)
        
        if rate_type == RateType.PERSON and 'user_id' not in data:
            return error_response("user_id es requerido para rate_type=person", 400)
        
        if rate_type == RateType.TASK and 'task_type' not in data:
            return error_response("task_type es requerido para rate_type=task", 400)
        
        if rate_type == RateType.ROLE and 'role' not in data:
            return error_response("role es requerido para rate_type=role", 400)
        
        # Validar que el proyecto pertenece a la organización
        if 'project_id' in data:
            project = Proyecto.query.filter_by(
                id=data['project_id'],
                organization_id=org_id
            ).first()
            if not project:
                return error_response("Proyecto no encontrado", 404)
        
        # Crear tarifa
        rate = Rate(
            organization_id=org_id,
            rate_type=rate_type,
            internal_cost=data['internal_cost'],
            billing_rate=data['billing_rate'],
            project_id=data.get('project_id'),
            user_id=data.get('user_id'),
            task_type=data.get('task_type'),
            role=data.get('role'),
            currency=data.get('currency', 'USD'),
            notes=data.get('notes'),
            created_by=user['id']
        )
        
        db.session.add(rate)
        db.session.commit()
        
        return success_response(
            data=rate.to_dict(),
            message="Tarifa creada exitosamente",
            status_code=201
        )
    
    except IntegrityError:
        db.session.rollback()
        return error_response("Ya existe una tarifa activa con estos parámetros", 409)
    
    except ValueError as e:
        return error_response(str(e), 400)
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@rates_bp.route('/<int:rate_id>', methods=['PUT'])
@organization_required
@requires_permission('MANAGE_FINANCIAL_DATA')
def update_rate(rate_id):
    """Actualiza una tarifa"""
    try:
        org_id = get_current_organization()
        rate = Rate.query.filter_by(id=rate_id, organization_id=org_id).first()
        
        if not rate:
            return error_response("Tarifa no encontrada", 404)
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'internal_cost' in data:
            rate.internal_cost = data['internal_cost']
        
        if 'billing_rate' in data:
            rate.billing_rate = data['billing_rate']
        
        if 'currency' in data:
            rate.currency = data['currency']
        
        if 'notes' in data:
            rate.notes = data['notes']
        
        if 'is_active' in data:
            rate.is_active = data['is_active']
        
        db.session.commit()
        
        return success_response(
            data=rate.to_dict(),
            message="Tarifa actualizada exitosamente"
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@rates_bp.route('/<int:rate_id>', methods=['DELETE'])
@organization_required
@requires_permission('MANAGE_FINANCIAL_DATA')
def delete_rate(rate_id):
    """Desactiva una tarifa (soft delete)"""
    try:
        org_id = get_current_organization()
        rate = Rate.query.filter_by(id=rate_id, organization_id=org_id).first()
        
        if not rate:
            return error_response("Tarifa no encontrada", 404)
        
        rate.is_active = False
        db.session.commit()
        
        return success_response(message="Tarifa desactivada exitosamente")
    
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@rates_bp.route('/effective', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_effective_rate():
    """
    Obtiene la tarifa efectiva según la jerarquía
    Query params:
        - project_id: requerido
        - user_id: opcional
        - task_type: opcional
    """
    try:
        org_id = get_current_organization()
        
        project_id = request.args.get('project_id', type=int)
        if not project_id:
            return error_response("project_id es requerido", 400)
        
        user_id = request.args.get('user_id', type=int)
        task_type = request.args.get('task_type')
        
        rate = Rate.get_effective_rate(
            organization_id=org_id,
            project_id=project_id,
            user_id=user_id,
            task_type=task_type
        )
        
        if not rate:
            return error_response("No se encontró una tarifa efectiva", 404)
        
        return success_response(
            data={
                **rate.to_dict(),
                'margin_percentage': rate.calculate_margin(),
                'profit_per_hour': float(rate.calculate_profit_per_hour())
            }
        )
    
    except Exception as e:
        return error_response(str(e), 500)

@rates_bp.route('/project/<int:project_id>/hierarchy', methods=['GET'])
@organization_required
@requires_permission('VIEW_FINANCIAL_DATA')
def get_rate_hierarchy(project_id):
    """
    Muestra todas las tarifas aplicables al proyecto en orden de prioridad
    """
    try:
        org_id = get_current_organization()
        
        # Verificar proyecto
        project = Proyecto.query.filter_by(id=project_id, organization_id=org_id).first()
        if not project:
            return error_response("Proyecto no encontrado", 404)
        
        hierarchy = []
        
        # 1. Tarifas por tarea
        task_rates = Rate.query.filter_by(
            organization_id=org_id,
            rate_type=RateType.TASK,
            is_active=True
        ).all()
        
        if task_rates:
            hierarchy.append({
                'priority': 1,
                'type': 'task',
                'rates': [r.to_dict() for r in task_rates]
            })
        
        # 2. Tarifas por persona en el proyecto
        person_rates = Rate.query.filter_by(
            organization_id=org_id,
            rate_type=RateType.PERSON,
            project_id=project_id,
            is_active=True
        ).all()
        
        if person_rates:
            hierarchy.append({
                'priority': 2,
                'type': 'person',
                'rates': [r.to_dict() for r in person_rates]
            })
        
        # 3. Tarifa del proyecto
        project_rate = Rate.query.filter_by(
            organization_id=org_id,
            rate_type=RateType.PROJECT,
            project_id=project_id,
            is_active=True
        ).first()
        
        if project_rate:
            hierarchy.append({
                'priority': 3,
                'type': 'project',
                'rates': [project_rate.to_dict()]
            })
        
        # 4. Tarifas por rol
        role_rates = Rate.query.filter_by(
            organization_id=org_id,
            rate_type=RateType.ROLE,
            is_active=True
        ).all()
        
        if role_rates:
            hierarchy.append({
                'priority': 4,
                'type': 'role',
                'rates': [r.to_dict() for r in role_rates]
            })
        
        return success_response(
            data={
                'project_id': project_id,
                'project_name': project.nombre,
                'hierarchy': hierarchy
            }
        )
    
    except Exception as e:
        return error_response(str(e), 500)
