"""
Servicio de Rentabilidad (Profitability)
Cálculos financieros en tiempo real
Fase 3: Motor Financiero
"""

from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import func, case
from app import db
from app.models.rate import Rate, RateType
from app.models.budget import Budget, BudgetType
from app.models.project_expense import ProjectExpense
from app.models.dia import Dia
from app.models.proyecto import Proyecto
from app.models.tarea import Tarea

class ProfitabilityService:
    """
    Servicio para cálculos de rentabilidad y métricas financieras
    """

    @staticmethod
    def calculate_project_profitability(project_id: int) -> Dict:
        """
        Calcula la rentabilidad completa de un proyecto
        
        Returns:
            {
                'total_hours': float,
                'billable_hours': float,
                'non_billable_hours': float,
                'internal_cost': float,
                'billable_revenue': float,
                'additional_expenses': float,
                'net_profit': float,
                'profit_margin': float,
                'health_status': str
            }
        """
        # Obtener proyecto
        project = Proyecto.query.get(project_id)
        if not project:
            raise ValueError(f"Proyecto {project_id} no encontrado")

        # Obtener tarifa del proyecto
        rate = Rate.get_effective_rate(
            organization_id=project.organization_id,
            project_id=project_id
        )
        
        if not rate:
            # Sin tarifa configurada, retornar ceros
            return {
                'total_hours': 0,
                'billable_hours': 0,
                'non_billable_hours': 0,
                'internal_cost': 0,
                'billable_revenue': 0,
                'additional_expenses': 0,
                'net_profit': 0,
                'profit_margin': 0,
                'health_status': 'no_rate_configured',
                'currency': 'USD'
            }

        # Calcular horas totales y facturables
        dias = Dia.query.filter_by(proyecto_id=project_id).all()
        
        total_hours = sum(dia.horas_trabajadas or 0 for dia in dias)
        billable_hours = sum(
            dia.horas_trabajadas or 0 
            for dia in dias 
            if getattr(dia, 'is_billable', True)
        )
        non_billable_hours = total_hours - billable_hours

        # Cálculos financieros
        internal_cost = float(total_hours * rate.internal_cost)
        billable_revenue = float(billable_hours * rate.billing_rate)
        
        # Gastos adicionales
        additional_expenses = ProjectExpense.get_project_total(project_id)
        
        # Ganancia neta
        net_profit = billable_revenue - internal_cost - additional_expenses
        
        # Margen de ganancia
        profit_margin = 0
        if billable_revenue > 0:
            profit_margin = (net_profit / billable_revenue) * 100

        # Estado de salud
        health_status = ProfitabilityService._get_profitability_health(profit_margin)

        return {
            'total_hours': round(total_hours, 2),
            'billable_hours': round(billable_hours, 2),
            'non_billable_hours': round(non_billable_hours, 2),
            'internal_cost': round(internal_cost, 2),
            'billable_revenue': round(billable_revenue, 2),
            'additional_expenses': round(additional_expenses, 2),
            'net_profit': round(net_profit, 2),
            'profit_margin': round(profit_margin, 2),
            'health_status': health_status,
            'currency': rate.currency
        }

    @staticmethod
    def calculate_organization_profitability(organization_id: int) -> Dict:
        """
        Calcula rentabilidad total de una organización
        """
        projects = Proyecto.query.filter_by(organization_id=organization_id).all()
        
        total_revenue = 0
        total_cost = 0
        total_expenses = 0
        total_hours = 0
        billable_hours = 0

        for project in projects:
            prof = ProfitabilityService.calculate_project_profitability(project.id)
            total_revenue += prof['billable_revenue']
            total_cost += prof['internal_cost']
            total_expenses += prof['additional_expenses']
            total_hours += prof['total_hours']
            billable_hours += prof['billable_hours']

        net_profit = total_revenue - total_cost - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'total_projects': len(projects),
            'total_hours': round(total_hours, 2),
            'billable_hours': round(billable_hours, 2),
            'billable_percentage': round((billable_hours / total_hours * 100) if total_hours > 0 else 0, 2),
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'total_expenses': round(total_expenses, 2),
            'net_profit': round(net_profit, 2),
            'profit_margin': round(profit_margin, 2),
            'health_status': ProfitabilityService._get_profitability_health(profit_margin)
        }

    @staticmethod
    def calculate_monthly_profitability(organization_id: int, year: int, month: int) -> Dict:
        """
        Calcula rentabilidad del mes
        """
        from calendar import monthrange
        
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        # Obtener días del mes
        dias = Dia.query.join(Proyecto).filter(
            Proyecto.organization_id == organization_id,
            Dia.fecha >= start_date,
            Dia.fecha <= end_date
        ).all()

        # Agrupar por proyecto
        projects_data = {}
        for dia in dias:
            if dia.proyecto_id not in projects_data:
                projects_data[dia.proyecto_id] = {
                    'hours': 0,
                    'billable_hours': 0
                }
            
            projects_data[dia.proyecto_id]['hours'] += dia.horas_trabajadas or 0
            if getattr(dia, 'is_billable', True):
                projects_data[dia.proyecto_id]['billable_hours'] += dia.horas_trabajadas or 0

        # Calcular totales
        total_revenue = 0
        total_cost = 0
        
        for project_id, data in projects_data.items():
            rate = Rate.get_effective_rate(organization_id=organization_id, project_id=project_id)
            if rate:
                total_cost += data['hours'] * float(rate.internal_cost)
                total_revenue += data['billable_hours'] * float(rate.billing_rate)

        net_profit = total_revenue - total_cost
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

        return {
            'year': year,
            'month': month,
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'net_profit': round(net_profit, 2),
            'profit_margin': round(profit_margin, 2)
        }

    @staticmethod
    def get_budget_health(project_id: int) -> Dict:
        """
        Obtiene el estado de salud del presupuesto
        """
        budget = Budget.query.filter_by(project_id=project_id).first()
        
        if not budget:
            return {
                'has_budget': False,
                'message': 'Proyecto sin presupuesto configurado'
            }

        burn_rate = budget.calculate_burn_rate()
        remaining = budget.calculate_remaining()
        health = budget.get_health_status()

        return {
            'has_budget': True,
            'budget_type': budget.budget_type.value,
            'total_amount': float(budget.total_amount) if budget.total_amount else None,
            'total_hours': float(budget.total_hours) if budget.total_hours else None,
            'consumed_amount': float(budget.consumed_amount),
            'consumed_hours': float(budget.consumed_hours),
            'additional_expenses': float(budget.additional_expenses),
            'burn_rate': round(burn_rate, 2),
            'remaining': remaining,
            'health_status': health,
            'is_exceeded': budget.is_exceeded,
            'alert_threshold': budget.alert_threshold_percentage,
            'should_alert': budget.should_send_alert()
        }

    @staticmethod
    def get_projects_at_risk(organization_id: int, threshold: float = 85.0) -> List[Dict]:
        """
        Obtiene proyectos con burn rate por encima del threshold
        """
        budgets = Budget.query.join(Proyecto).filter(
            Proyecto.organization_id == organization_id,
            Budget.is_exceeded == False
        ).all()

        at_risk = []
        for budget in budgets:
            burn_rate = budget.calculate_burn_rate()
            if burn_rate >= threshold:
                at_risk.append({
                    'project_id': budget.project_id,
                    'project_name': budget.project.nombre,
                    'burn_rate': round(burn_rate, 2),
                    'health_status': budget.get_health_status(),
                    'remaining': budget.calculate_remaining()
                })

        return sorted(at_risk, key=lambda x: x['burn_rate'], reverse=True)

    @staticmethod
    def calculate_employee_cost(user_id: int, project_id: int, hours: float) -> Dict:
        """
        Calcula el costo de un empleado en un proyecto
        """
        from app.models.proyecto import Proyecto
        
        project = Proyecto.query.get(project_id)
        if not project:
            raise ValueError(f"Proyecto {project_id} no encontrado")

        rate = Rate.get_effective_rate(
            organization_id=project.organization_id,
            project_id=project_id,
            user_id=user_id
        )

        if not rate:
            return {
                'user_id': user_id,
                'hours': hours,
                'internal_cost': 0,
                'billing_rate': 0,
                'message': 'Sin tarifa configurada'
            }

        internal_cost = hours * float(rate.internal_cost)
        billing_revenue = hours * float(rate.billing_rate)
        profit = billing_revenue - internal_cost

        return {
            'user_id': user_id,
            'hours': hours,
            'internal_cost': round(internal_cost, 2),
            'billing_revenue': round(billing_revenue, 2),
            'profit': round(profit, 2),
            'profit_margin': round((profit / billing_revenue * 100) if billing_revenue > 0 else 0, 2)
        }

    @staticmethod
    def _get_profitability_health(profit_margin: float) -> str:
        """
        Determina el estado de salud según el margen
        """
        if profit_margin >= 30:
            return 'healthy'  # Verde
        elif profit_margin >= 10:
            return 'warning'  # Amarillo
        elif profit_margin >= 0:
            return 'critical'  # Naranja
        else:
            return 'losing_money'  # Rojo (pérdida)

    @staticmethod
    def get_expense_summary(project_id: int) -> Dict:
        """
        Resumen de gastos del proyecto
        """
        expenses = ProjectExpense.query.filter_by(
            project_id=project_id,
            is_approved=True
        ).all()

        by_category = {}
        total_billable = 0
        total_non_billable = 0

        for expense in expenses:
            category = expense.category.value
            amount = float(expense.amount)
            
            if category not in by_category:
                by_category[category] = 0
            by_category[category] += amount

            if expense.is_billable:
                total_billable += amount
            else:
                total_non_billable += amount

        return {
            'total_expenses': round(total_billable + total_non_billable, 2),
            'billable_expenses': round(total_billable, 2),
            'non_billable_expenses': round(total_non_billable, 2),
            'by_category': {k: round(v, 2) for k, v in by_category.items()},
            'count': len(expenses)
        }
