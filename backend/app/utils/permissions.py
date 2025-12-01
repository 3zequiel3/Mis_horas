"""
Sistema de Permisos Granulares RBAC
Define permisos específicos y su mapeo a roles
"""

from enum import Enum
from typing import Set, Dict, List


class Permission(str, Enum):
    """Permisos específicos del sistema"""
    
    # === ORGANIZACIÓN ===
    DELETE_ORGANIZATION = "delete_organization"  # Solo Owner
    TRANSFER_OWNERSHIP = "transfer_ownership"  # Solo Owner
    CHANGE_PLAN = "change_plan"  # Solo Owner
    
    # === GESTIÓN DE USUARIOS ===
    INVITE_MEMBERS = "invite_members"  # Owner, Admin
    REMOVE_MEMBERS = "remove_members"  # Owner, Admin
    CHANGE_ROLES = "change_roles"  # Owner, Admin
    VIEW_ALL_MEMBERS = "view_all_members"  # Owner, Admin, Manager
    
    # === PROYECTOS ===
    CREATE_PROJECT = "create_project"  # Owner, Admin, Manager
    DELETE_PROJECT = "delete_project"  # Owner, Admin
    EDIT_PROJECT = "edit_project"  # Owner, Admin, Manager
    VIEW_ALL_PROJECTS = "view_all_projects"  # Owner, Admin, Manager
    VIEW_ASSIGNED_PROJECTS = "view_assigned_projects"  # Todos
    
    # === DATOS FINANCIEROS ===
    VIEW_GLOBAL_COSTS = "view_global_costs"  # Owner, Admin
    VIEW_PROJECT_COSTS = "view_project_costs"  # Owner, Admin
    VIEW_EMPLOYEE_RATES = "view_employee_rates"  # Owner, Admin
    EDIT_EMPLOYEE_RATES = "edit_employee_rates"  # Owner, Admin
    VIEW_PROJECT_BUDGET = "view_project_budget"  # Owner, Admin, Manager
    VIEW_PROFITABILITY = "view_profitability"  # Owner, Admin, Manager
    
    # === GESTIÓN DE TIEMPO ===
    LOG_OWN_TIME = "log_own_time"  # Todos
    EDIT_OWN_TIME = "edit_own_time"  # Todos (con restricciones de estado)
    VIEW_OWN_TIME = "view_own_time"  # Todos
    VIEW_TEAM_TIME = "view_team_time"  # Owner, Admin, Manager
    EDIT_TEAM_TIME = "edit_team_time"  # Owner, Admin
    DELETE_TIME_ENTRIES = "delete_time_entries"  # Owner, Admin
    
    # === APROBACIONES ===
    SUBMIT_TIME_FOR_APPROVAL = "submit_time_for_approval"  # Member, Manager
    APPROVE_TIME = "approve_time"  # Manager, Admin, Owner
    REJECT_TIME = "reject_time"  # Manager, Admin, Owner
    REOPEN_APPROVED_TIME = "reopen_approved_time"  # Owner, Admin
    LOCK_TIME_PERIOD = "lock_time_period"  # Admin, Owner
    
    # === TAREAS Y ASIGNACIONES ===
    CREATE_TASK = "create_task"  # Todos en proyectos asignados
    EDIT_OWN_TASKS = "edit_own_tasks"  # Todos
    EDIT_ALL_TASKS = "edit_all_tasks"  # Owner, Admin, Manager
    DELETE_TASK = "delete_task"  # Owner, Admin, Manager
    ASSIGN_TASKS = "assign_tasks"  # Owner, Admin, Manager
    
    # === EMPLEADOS ===
    ADD_EMPLOYEE = "add_employee"  # Owner, Admin, Manager
    REMOVE_EMPLOYEE = "remove_employee"  # Owner, Admin
    EDIT_EMPLOYEE = "edit_employee"  # Owner, Admin, Manager
    VIEW_EMPLOYEE_DETAILS = "view_employee_details"  # Owner, Admin, Manager
    
    # === REPORTES Y AUDITORÍA ===
    VIEW_AUDIT_LOG = "view_audit_log"  # Owner, Admin
    EXPORT_REPORTS = "export_reports"  # Owner, Admin, Manager
    VIEW_ANALYTICS = "view_analytics"  # Owner, Admin, Manager
    
    # === CONFIGURACIÓN ===
    EDIT_ORGANIZATION_SETTINGS = "edit_organization_settings"  # Owner, Admin
    EDIT_PROJECT_SETTINGS = "edit_project_settings"  # Owner, Admin, Manager (project leader)
    CONFIGURE_ATTENDANCE = "configure_attendance"  # Owner, Admin, Manager


# Mapeo de Roles a Permisos
ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    "owner": {
        # El Owner tiene TODOS los permisos
        *list(Permission)
    },
    
    "admin": {
        # Administrador: Todos excepto acciones de Owner
        Permission.INVITE_MEMBERS,
        Permission.REMOVE_MEMBERS,
        Permission.CHANGE_ROLES,
        Permission.VIEW_ALL_MEMBERS,
        Permission.CREATE_PROJECT,
        Permission.DELETE_PROJECT,
        Permission.EDIT_PROJECT,
        Permission.VIEW_ALL_PROJECTS,
        Permission.VIEW_ASSIGNED_PROJECTS,
        Permission.VIEW_GLOBAL_COSTS,
        Permission.VIEW_PROJECT_COSTS,
        Permission.VIEW_EMPLOYEE_RATES,
        Permission.EDIT_EMPLOYEE_RATES,
        Permission.VIEW_PROJECT_BUDGET,
        Permission.VIEW_PROFITABILITY,
        Permission.LOG_OWN_TIME,
        Permission.EDIT_OWN_TIME,
        Permission.VIEW_OWN_TIME,
        Permission.VIEW_TEAM_TIME,
        Permission.EDIT_TEAM_TIME,
        Permission.DELETE_TIME_ENTRIES,
        Permission.APPROVE_TIME,
        Permission.REJECT_TIME,
        Permission.REOPEN_APPROVED_TIME,
        Permission.LOCK_TIME_PERIOD,
        Permission.CREATE_TASK,
        Permission.EDIT_OWN_TASKS,
        Permission.EDIT_ALL_TASKS,
        Permission.DELETE_TASK,
        Permission.ASSIGN_TASKS,
        Permission.ADD_EMPLOYEE,
        Permission.REMOVE_EMPLOYEE,
        Permission.EDIT_EMPLOYEE,
        Permission.VIEW_EMPLOYEE_DETAILS,
        Permission.VIEW_AUDIT_LOG,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_ANALYTICS,
        Permission.EDIT_ORGANIZATION_SETTINGS,
        Permission.EDIT_PROJECT_SETTINGS,
        Permission.CONFIGURE_ATTENDANCE,
    },
    
    "manager": {
        # Manager: Gestión táctica, ve presupuestos pero no salarios individuales
        Permission.VIEW_ALL_MEMBERS,
        Permission.CREATE_PROJECT,
        Permission.EDIT_PROJECT,
        Permission.VIEW_ALL_PROJECTS,
        Permission.VIEW_ASSIGNED_PROJECTS,
        Permission.VIEW_PROJECT_BUDGET,  # Ve agregados, no salarios
        Permission.VIEW_PROFITABILITY,
        Permission.LOG_OWN_TIME,
        Permission.EDIT_OWN_TIME,
        Permission.VIEW_OWN_TIME,
        Permission.VIEW_TEAM_TIME,
        Permission.SUBMIT_TIME_FOR_APPROVAL,
        Permission.APPROVE_TIME,
        Permission.REJECT_TIME,
        Permission.CREATE_TASK,
        Permission.EDIT_OWN_TASKS,
        Permission.EDIT_ALL_TASKS,
        Permission.DELETE_TASK,
        Permission.ASSIGN_TASKS,
        Permission.ADD_EMPLOYEE,
        Permission.EDIT_EMPLOYEE,
        Permission.VIEW_EMPLOYEE_DETAILS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_ANALYTICS,
        Permission.EDIT_PROJECT_SETTINGS,
        Permission.CONFIGURE_ATTENDANCE,
    },
    
    "member": {
        # Miembro/Empleado: Visión de túnel, solo sus proyectos
        Permission.VIEW_ASSIGNED_PROJECTS,
        Permission.LOG_OWN_TIME,
        Permission.EDIT_OWN_TIME,
        Permission.VIEW_OWN_TIME,
        Permission.SUBMIT_TIME_FOR_APPROVAL,
        Permission.CREATE_TASK,
        Permission.EDIT_OWN_TASKS,
    },
    
    "viewer": {
        # Invitado/Cliente: Solo lectura
        Permission.VIEW_ASSIGNED_PROJECTS,
        Permission.VIEW_OWN_TIME,
    }
}


def has_permission(role: str, permission: Permission) -> bool:
    """
    Verifica si un rol tiene un permiso específico
    
    Args:
        role: Rol del usuario (owner, admin, manager, member, viewer)
        permission: Permiso a verificar
        
    Returns:
        bool: True si el rol tiene el permiso
    """
    if role not in ROLE_PERMISSIONS:
        return False
    return permission in ROLE_PERMISSIONS[role]


def get_role_permissions(role: str) -> Set[Permission]:
    """
    Obtiene todos los permisos de un rol
    
    Args:
        role: Rol del usuario
        
    Returns:
        Set[Permission]: Conjunto de permisos del rol
    """
    return ROLE_PERMISSIONS.get(role, set())


def can_user_access_financial_data(role: str, data_type: str = "costs") -> bool:
    """
    Verifica si un usuario puede ver datos financieros
    
    Args:
        role: Rol del usuario
        data_type: Tipo de dato (costs, rates, budget, profitability)
        
    Returns:
        bool: True si puede ver los datos
    """
    permission_map = {
        "costs": Permission.VIEW_GLOBAL_COSTS,
        "rates": Permission.VIEW_EMPLOYEE_RATES,
        "budget": Permission.VIEW_PROJECT_BUDGET,
        "profitability": Permission.VIEW_PROFITABILITY
    }
    
    permission = permission_map.get(data_type)
    if not permission:
        return False
        
    return has_permission(role, permission)


def can_modify_time_entry(role: str, entry_status: str, is_own_entry: bool = True) -> bool:
    """
    Verifica si un usuario puede modificar una entrada de tiempo
    según su estado y propiedad
    
    Args:
        role: Rol del usuario
        entry_status: Estado de la entrada (draft, pending, approved, rejected)
        is_own_entry: Si la entrada pertenece al usuario
        
    Returns:
        bool: True si puede modificar
    """
    # Entradas aprobadas: solo Owner y Admin pueden reabrir
    if entry_status == "approved":
        return has_permission(role, Permission.REOPEN_APPROVED_TIME)
    
    # Entradas pendientes: no se pueden editar, deben ser aprobadas/rechazadas
    if entry_status == "pending":
        return False
    
    # Entradas propias en borrador o rechazadas
    if is_own_entry and entry_status in ["draft", "rejected"]:
        return has_permission(role, Permission.EDIT_OWN_TIME)
    
    # Entradas de otros
    if not is_own_entry:
        return has_permission(role, Permission.EDIT_TEAM_TIME)
    
    return False


def is_personal_mode(organization_type: str) -> bool:
    """
    Determina si la organización está en modo personal/freelance
    
    Args:
        organization_type: Tipo de organización (personal, freelance, empresa, agencia)
        
    Returns:
        bool: True si es modo personal
    """
    return organization_type in ["personal", "freelance"]


def get_simplified_permissions_for_personal_mode() -> Set[Permission]:
    """
    Retorna permisos simplificados para modo personal
    En modo personal, el usuario tiene casi todos los permisos automáticamente
    """
    return {
        Permission.CREATE_PROJECT,
        Permission.EDIT_PROJECT,
        Permission.DELETE_PROJECT,
        Permission.VIEW_ALL_PROJECTS,
        Permission.VIEW_GLOBAL_COSTS,
        Permission.VIEW_PROJECT_COSTS,
        Permission.VIEW_EMPLOYEE_RATES,
        Permission.EDIT_EMPLOYEE_RATES,
        Permission.VIEW_PROJECT_BUDGET,
        Permission.VIEW_PROFITABILITY,
        Permission.LOG_OWN_TIME,
        Permission.EDIT_OWN_TIME,
        Permission.VIEW_OWN_TIME,
        Permission.VIEW_TEAM_TIME,
        Permission.EDIT_TEAM_TIME,
        Permission.CREATE_TASK,
        Permission.EDIT_OWN_TASKS,
        Permission.EDIT_ALL_TASKS,
        Permission.DELETE_TASK,
        Permission.ASSIGN_TASKS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_ANALYTICS,
    }
