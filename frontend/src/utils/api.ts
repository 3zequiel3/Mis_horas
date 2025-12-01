/**
 * API Configuration
 * Configuración centralizada para todas las llamadas a la API
 */

// URL base de la API
export const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || 'http://localhost:22000';

// Endpoints principales
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/api/login',
  REGISTER: '/api/register',
  LOGOUT: '/api/logout',
  
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
  let token: string | null = null;
  let orgId: string | null = null;
  
  // IMPORTANTE: Buscar en sessionStorage Y localStorage (AuthService puede usar ambos)
  if (typeof window !== 'undefined') {
    // Buscar token en las keys que usa AuthService
    // PRIMERO sessionStorage (sesión actual), LUEGO localStorage (remember me)
    token = sessionStorage.getItem('auth_token_session') || 
            localStorage.getItem('auth_token_persist') ||
            localStorage.getItem('token'); // Mantener compatibilidad con código legacy
    
    orgId = localStorage.getItem('currentOrganizationId');
    
    console.log('[getAuthHeaders] Tokens encontrados:', {
      session: !!sessionStorage.getItem('auth_token_session'),
      persist: !!localStorage.getItem('auth_token_persist'),
      legacy: !!localStorage.getItem('token'),
      orgId: !!orgId
    });
  }
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  } else {
    console.error('[getAuthHeaders] ⚠️ ERROR: No se encontró token en sessionStorage ni localStorage');
  }
  
  if (orgId) {
    headers['X-Organization-ID'] = orgId;
  } else {
    console.warn('[getAuthHeaders] ⚠️ No se encontró orgId');
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
      errorMessage = errorData.message || errorData.error || errorMessage;
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
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers,
    },
  };
  
  const response = await fetch(url, config);
  return handleApiResponse<T>(response);
}
