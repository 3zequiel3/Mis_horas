/**
 * Servicio de API para Auditoría
 */

import { apiFetch, API_ENDPOINTS } from '../utils/api';
import type {
  AuditLog,
  AuditLogFilters,
  AuditLogResponse,
  AuditStatistics,
} from '../types/audit';

export const auditService = {
  /**
   * Obtiene logs de auditoría con filtros
   */
  async getLogs(filters: AuditLogFilters = {}): Promise<AuditLogResponse> {
    const params = new URLSearchParams();

    // IMPORTANTE: proyecto_id es requerido
    if (filters.proyecto_id) params.append('proyecto_id', filters.proyecto_id.toString());
    if (filters.action) params.append('action', filters.action);
    if (filters.category) params.append('category', filters.category);
    if (filters.user_id) params.append('user_id', filters.user_id.toString());
    if (filters.resource_type) params.append('resource_type', filters.resource_type);
    if (filters.severity) params.append('severity', filters.severity);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.per_page) params.append('per_page', filters.per_page.toString());

    const queryString = params.toString();
    const url = queryString ? `${API_ENDPOINTS.AUDIT_LOGS}?${queryString}` : API_ENDPOINTS.AUDIT_LOGS;
    
    return apiFetch<AuditLogResponse>(url);
  },

  /**
   * Obtiene un log específico por ID
   */
  async getLog(id: number): Promise<AuditLog> {
    const result = await apiFetch<{ log: AuditLog }>(`${API_ENDPOINTS.AUDIT_LOGS}/${id}`);
    
    if (!result.log) {
      throw new Error('Log de auditoría no encontrado');
    }
    return result.log;
  },

  /**
   * Obtiene estadísticas de auditoría
   */
  async getStatistics(filters?: AuditLogFilters): Promise<AuditStatistics> {
    const params = new URLSearchParams();

    if (filters?.start_date) params.append('start_date', filters.start_date);
    if (filters?.end_date) params.append('end_date', filters.end_date);
    if (filters?.category) params.append('category', filters.category);

    const queryString = params.toString();
    const url = queryString 
      ? `${API_ENDPOINTS.AUDIT_LOGS}/statistics?${queryString}` 
      : `${API_ENDPOINTS.AUDIT_LOGS}/statistics`;
    
    return apiFetch<AuditStatistics>(url);
  },

  /**
   * Exporta logs de auditoría
   */
  async exportLogs(filters: AuditLogFilters = {}, format: 'csv' | 'json' = 'csv'): Promise<Blob> {
    const params = new URLSearchParams();

    if (filters.action) params.append('action', filters.action);
    if (filters.category) params.append('category', filters.category);
    if (filters.user_id) params.append('user_id', filters.user_id.toString());
    if (filters.resource_type) params.append('resource_type', filters.resource_type);
    if (filters.severity) params.append('severity', filters.severity);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    params.append('format', format);

    const queryString = params.toString();
    const url = `${API_ENDPOINTS.AUDIT_LOGS}/export?${queryString}`;

    const token = localStorage.getItem('token');
    const orgId = localStorage.getItem('currentOrganizationId');
    
    const headers: HeadersInit = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (orgId) headers['X-Organization-ID'] = orgId;

    const API_BASE_URL_LOCAL = import.meta.env.PUBLIC_API_BASE_URL || 'http://localhost:22000';
    const response = await fetch(`${API_BASE_URL_LOCAL}${url}`, {
      headers
    });

    if (!response.ok) {
      throw new Error('Error al exportar logs');
    }

    return response.blob();
  }
};
