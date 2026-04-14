/**
 * API Configuration
 * Configuración centralizada para todas las llamadas a la API
 */

import { AuthService } from '../services/auth';
import { $currentOrganizationId } from '../stores/organizationStore';

// URL base de la API
export const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || 'http://localhost:22000';

// Endpoints principales
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/api/auth/login',
  REGISTER: '/api/auth/register',
  LOGOUT: '/api/auth/logout',
  // Deprecated aliases (kept for compatibility during migration)
  LOGIN_LEGACY: '/api/login',
  REGISTER_LEGACY: '/api/register',
  LOGOUT_LEGACY: '/api/logout',
  
  // Usuarios
  USUARIOS: '/api/usuarios',
  USUARIO_ACTUAL: '/api/usuarios/me',
  
  // Proyectos
  PROYECTOS: '/api/proyectos',
  PROYECTO: (id: number) => `/api/proyectos/${id}`,
  
  // Tareas
  TAREAS: (projectId: number) => `/api/proyectos/${projectId}/tareas`,
  TAREA: (projectId: number, taskId: number) => `/api/proyectos/${projectId}/tareas/${taskId}`,
  
  // Organizaciones
  ORGANIZACIONES: '/api/organizations',
  ORGANIZACION: (id: number) => `/api/organizations/${id}`,
  ORGANIZACION_MIEMBROS: (id: number) => `/api/organizations/${id}/members`,
  ORGANIZACION_PROYECTOS: (id: number) => `/api/organizations/${id}/projects`,
  
  // Budget Addons (Fase 4)
  PROJECT_BUDGET_ADDONS: (projectId: number) => `/api/projects/${projectId}/budget-addons`,
  PROJECT_BUDGET_ADDON: (projectId: number, addonId: number) => `/api/projects/${projectId}/budget-addons/${addonId}`,
  PROJECT_TOTAL_BUDGET: (projectId: number) => `/api/projects/${projectId}/total-budget`,
  
  // Rates (Fase 3)
  PROJECT_RATES: (projectId: number) => `/api/projects/${projectId}/rates`,
  PROJECT_RATE: (projectId: number, rateId: number) => `/api/projects/${projectId}/rates/${rateId}`,
  
  // Budgets (Fase 3)
  PROJECT_BUDGETS: (projectId: number) => `/api/projects/${projectId}/budgets`,
  PROJECT_BUDGET: (projectId: number, budgetId: number) => `/api/projects/${projectId}/budgets/${budgetId}`,
  
  // Expenses (Fase 3)
  PROJECT_EXPENSES: (projectId: number) => `/api/projects/${projectId}/expenses`,
  PROJECT_EXPENSE: (projectId: number, expenseId: number) => `/api/projects/${projectId}/expenses/${expenseId}`,
  
  // Profitability (Fase 3)
  PROJECT_PROFITABILITY: (projectId: number) => `/api/profitability/project/${projectId}`,
  PROJECT_BUDGET_HEALTH: (projectId: number) => `/api/profitability/project/${projectId}/budget-health`,
  
  // Audit (Fase 3)
  AUDIT_LOGS: '/api/auditoria/logs',
  
  // Approvals (Fase 3)
  APPROVALS: '/api/aprobaciones',
};

/**
 * Obtiene los headers de autenticación
 */
export function getAuthHeaders(): HeadersInit {
  const token = AuthService.getToken();
  let orgId: string | null = null;

  const currentOrg = $currentOrganizationId.get();
  if (currentOrg) {
    orgId = String(currentOrg);
  } else if (typeof window !== 'undefined') {
    orgId = localStorage.getItem('currentOrganizationId');
  }
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  if (orgId) {
    headers['X-Organization-ID'] = orgId;
  }
  
  return headers;
}

/**
 * Maneja respuestas de la API de forma consistente
 */
export async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `Error ${response.status}`;
    
    try {
      const errorData = await response.json();

      if (response.status === 422) {
        const detail = errorData?.detail;

        if (Array.isArray(detail) && detail.length > 0) {
          const first = detail[0];
          const field = Array.isArray(first?.loc) ? first.loc.join('.') : 'campo';
          const detailMessage = first?.msg || 'valor inválido';
          errorMessage = `${field}: ${detailMessage}`;
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else {
          errorMessage = errorData.message || errorData.error || 'Error de validación';
        }
      } else {
        errorMessage = errorData.message || errorData.error || errorMessage;
      }
    } catch (e) {
      // Si no se puede parsear el JSON, usar mensaje por defecto
      console.error('[handleApiResponse] No se pudo parsear error JSON:', e);
    }
    
    console.error(`[handleApiResponse] Error ${response.status}: ${errorMessage}`);
    throw new Error(errorMessage);
  }
  
  const data = await response.json();
  return data.data || data;
}

/**
 * Wrapper para fetch con configuración estándar
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    credentials: 'include',
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers,
    },
  };
  
  const response = await fetch(url, config);
  return handleApiResponse<T>(response);
}
