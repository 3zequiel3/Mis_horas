/**
 * Tipos para Auditoría y Logs
 */

export type AuditAction =
  // Organizaciones
  | 'create_organization'
  | 'update_organization'
  | 'delete_organization'
  | 'invite_member'
  | 'remove_member'
  | 'update_member_role'
  // Usuarios
  | 'create_user'
  | 'update_user'
  | 'delete_user'
  | 'change_password'
  | 'login'
  | 'logout'
  | 'failed_login'
  // Proyectos
  | 'create_project'
  | 'update_project'
  | 'delete_project'
  | 'assign_employee'
  | 'remove_employee'
  // Tiempo
  | 'create_time_entry'
  | 'update_time_entry'
  | 'delete_time_entry'
  | 'submit_timesheet'
  | 'approve_timesheet'
  | 'reject_timesheet'
  | 'reopen_timesheet'
  | 'lock_period'
  // Tareas
  | 'create_task'
  | 'update_task'
  | 'delete_task'
  | 'complete_task'
  // Empleados
  | 'create_employee'
  | 'update_employee'
  | 'delete_employee'
  | 'update_hourly_rate'
  // Financiero
  | 'view_financial_report'
  | 'export_financial_data'
  | 'update_budget'
  // Seguridad
  | 'change_permissions'
  | 'access_denied'
  | 'security_alert'
  // Sistema
  | 'system_config'
  | 'backup'
  | 'restore';

export type AuditCategory =
  | 'organization'
  | 'user'
  | 'project'
  | 'time'
  | 'task'
  | 'employee'
  | 'financial'
  | 'security'
  | 'system';

export type AuditSeverity = 'info' | 'warning' | 'error' | 'critical';

export interface AuditLog {
  id: number;
  organization_id: number;
  user_id: number;
  action: AuditAction;
  action_category: AuditCategory;
  resource_type?: string;
  resource_id?: number;
  resource_name?: string;
  description: string;
  extra_data?: Record<string, any>;
  old_value?: Record<string, any>;
  new_value?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  severity: AuditSeverity;
  created_at: string;
  user?: {
    id: number;
    nombre: string;
    email: string;
  };
}

export interface AuditLogFilters {
  proyecto_id?: number; // Filtrar logs por proyecto específico
  action?: AuditAction;
  category?: AuditCategory;
  user_id?: number;
  resource_type?: string;
  severity?: AuditSeverity;
  start_date?: string;
  end_date?: string;
  page?: number;
  per_page?: number;
}

export interface AuditLogResponse {
  logs: AuditLog[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

export interface AuditStatistics {
  total_logs: number;
  by_category: Record<AuditCategory, number>;
  by_severity: Record<AuditSeverity, number>;
  by_user: Array<{
    user_id: number;
    user_name: string;
    count: number;
  }>;
  top_actions: Array<{
    action: AuditAction;
    count: number;
  }>;
}
