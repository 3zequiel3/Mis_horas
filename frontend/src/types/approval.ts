/**
 * Tipos para Aprobación de Períodos de Tiempo
 */

export type TimePeriodStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'locked';

export interface TimePeriod {
  id: number;
  organization_id: number;
  proyecto_id: number;
  empleado_id: number;
  anio: number;
  mes: number;
  fecha_inicio: string;
  fecha_fin: string;
  status: TimePeriodStatus;
  submitted_by?: number;
  submitted_at?: string;
  reviewed_by?: number;
  reviewed_at?: string;
  review_notes?: string;
  total_hours?: number;
  total_days?: number;
  days_count?: number;
  tasks_count?: number;
  empleado_nombre?: string;
  proyecto_nombre?: string;
  approved_by?: string;
  approval_date?: string;
  rejection_reason?: string;
  dias?: Array<{
    id: number;
    fecha: string;
    horas_trabajadas: number;
    status: TimePeriodStatus;
  }>;
  empleado?: {
    id: number;
    nombre: string;
  };
  proyecto?: {
    id: number;
    nombre: string;
  };
  submitter?: {
    id: number;
    nombre: string;
    email: string;
  };
  reviewer?: {
    id: number;
    nombre: string;
    email: string;
  };
}

export interface SubmitPeriodRequest {
  // No requiere body, el ID viene en la URL
}

export interface ApprovePeriodRequest {
  notes?: string;
  comments?: string;
}

export interface RejectPeriodRequest {
  notes?: string;
  reason?: string; // Motivo del rechazo
}

export interface ReopenPeriodRequest {
  reason: string; // Obligatorio
}

export interface PendingApprovalsSummary {
  total_pending: number;
  by_project: Array<{
    proyecto_id: number;
    proyecto_nombre: string;
    count: number;
  }>;
  by_employee: Array<{
    empleado_id: number;
    empleado_nombre: string;
    count: number;
  }>;
}

/**
 * Permisos del sistema
 */
export enum Permission {
  // Organizaciones
  MANAGE_ORGANIZATION = 'manage_organization',
  INVITE_MEMBERS = 'invite_members',
  REMOVE_MEMBERS = 'remove_members',
  CHANGE_MEMBER_ROLES = 'change_member_roles',
  
  // Proyectos
  CREATE_PROJECTS = 'create_projects',
  EDIT_ALL_PROJECTS = 'edit_all_projects',
  DELETE_PROJECTS = 'delete_projects',
  VIEW_ALL_PROJECTS = 'view_all_projects',
  ASSIGN_EMPLOYEES = 'assign_employees',
  
  // Tareas
  CREATE_TASKS = 'create_tasks',
  EDIT_ALL_TASKS = 'edit_all_tasks',
  DELETE_TASKS = 'delete_tasks',
  VIEW_ALL_TASKS = 'view_all_tasks',
  ASSIGN_TASKS = 'assign_tasks',
  
  // Tiempo
  EDIT_OWN_TIME = 'edit_own_time',
  EDIT_ALL_TIME = 'edit_all_time',
  DELETE_TIME_ENTRIES = 'delete_time_entries',
  VIEW_ALL_TIME = 'view_all_time',
  SUBMIT_TIMESHEETS = 'submit_timesheets',
  APPROVE_TIMESHEETS = 'approve_timesheets',
  REOPEN_LOCKED_PERIODS = 'reopen_locked_periods',
  LOCK_PERIODS = 'lock_periods',
  
  // Empleados
  MANAGE_EMPLOYEES = 'manage_employees',
  VIEW_ALL_EMPLOYEES = 'view_all_employees',
  EDIT_EMPLOYEE_RATES = 'edit_employee_rates',
  
  // Financiero
  VIEW_FINANCIAL_DATA = 'view_financial_data',
  EDIT_BUDGETS = 'edit_budgets',
  VIEW_HOURLY_RATES = 'view_hourly_rates',
  EXPORT_FINANCIAL_REPORTS = 'export_financial_reports',
  
  // Reportes
  VIEW_ALL_REPORTS = 'view_all_reports',
  EXPORT_REPORTS = 'export_reports',
  
  // Asistencia
  MANAGE_ATTENDANCE = 'manage_attendance',
  VIEW_ATTENDANCE = 'view_attendance',
  JUSTIFY_ABSENCES = 'justify_absences',
  
  // Auditoría
  VIEW_AUDIT_LOG = 'view_audit_log',
  EXPORT_AUDIT_LOG = 'export_audit_log',
  
  // Sistema
  MANAGE_SETTINGS = 'manage_settings',
  MANAGE_INTEGRATIONS = 'manage_integrations',
}

export type Role = 'owner' | 'admin' | 'manager' | 'member' | 'viewer';

export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  owner: Object.values(Permission),
  admin: [
    Permission.INVITE_MEMBERS,
    Permission.REMOVE_MEMBERS,
    Permission.CHANGE_MEMBER_ROLES,
    Permission.CREATE_PROJECTS,
    Permission.EDIT_ALL_PROJECTS,
    Permission.DELETE_PROJECTS,
    Permission.VIEW_ALL_PROJECTS,
    Permission.ASSIGN_EMPLOYEES,
    Permission.CREATE_TASKS,
    Permission.EDIT_ALL_TASKS,
    Permission.DELETE_TASKS,
    Permission.VIEW_ALL_TASKS,
    Permission.ASSIGN_TASKS,
    Permission.EDIT_OWN_TIME,
    Permission.EDIT_ALL_TIME,
    Permission.DELETE_TIME_ENTRIES,
    Permission.VIEW_ALL_TIME,
    Permission.SUBMIT_TIMESHEETS,
    Permission.APPROVE_TIMESHEETS,
    Permission.LOCK_PERIODS,
    Permission.MANAGE_EMPLOYEES,
    Permission.VIEW_ALL_EMPLOYEES,
    Permission.EDIT_EMPLOYEE_RATES,
    Permission.VIEW_FINANCIAL_DATA,
    Permission.EDIT_BUDGETS,
    Permission.VIEW_HOURLY_RATES,
    Permission.EXPORT_FINANCIAL_REPORTS,
    Permission.VIEW_ALL_REPORTS,
    Permission.EXPORT_REPORTS,
    Permission.MANAGE_ATTENDANCE,
    Permission.VIEW_ATTENDANCE,
    Permission.JUSTIFY_ABSENCES,
    Permission.VIEW_AUDIT_LOG,
    Permission.EXPORT_AUDIT_LOG,
    Permission.MANAGE_SETTINGS,
    Permission.MANAGE_INTEGRATIONS,
  ],
  manager: [
    Permission.CREATE_PROJECTS,
    Permission.VIEW_ALL_PROJECTS,
    Permission.ASSIGN_EMPLOYEES,
    Permission.CREATE_TASKS,
    Permission.EDIT_ALL_TASKS,
    Permission.VIEW_ALL_TASKS,
    Permission.ASSIGN_TASKS,
    Permission.EDIT_OWN_TIME,
    Permission.VIEW_ALL_TIME,
    Permission.SUBMIT_TIMESHEETS,
    Permission.APPROVE_TIMESHEETS,
    Permission.VIEW_ALL_EMPLOYEES,
    Permission.VIEW_ALL_REPORTS,
    Permission.EXPORT_REPORTS,
    Permission.VIEW_ATTENDANCE,
    Permission.JUSTIFY_ABSENCES,
  ],
  member: [
    Permission.EDIT_OWN_TIME,
    Permission.SUBMIT_TIMESHEETS,
    Permission.JUSTIFY_ABSENCES,
  ],
  viewer: [],
};
