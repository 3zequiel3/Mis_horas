/**
 * Servicio de API para Aprobación de Períodos de Tiempo
 */

import { apiFetch, API_ENDPOINTS } from '../utils/api';
import type {
  TimePeriod,
  ApprovePeriodRequest,
  RejectPeriodRequest,
  ReopenPeriodRequest,
  ApprovalHistory,
  PeriodActionResponse,
} from '../types/approval';

export const approvalService = {
  /**
   * Obtiene períodos de un proyecto (todos los empleados)
   */
  async getProjectPeriods(proyectoId: number, anio?: number, mes?: number): Promise<TimePeriod[]> {
    const params = new URLSearchParams();
    params.append('proyecto_id', proyectoId.toString());
    if (anio) params.append('anio', anio.toString());
    if (mes) params.append('mes', mes.toString());

    const queryString = params.toString();
    const url = `${API_ENDPOINTS.APPROVALS}/periods?${queryString}`;
    
    const result = await apiFetch<{ periods: TimePeriod[] }>(url);
    return result.periods || [];
  },

  /**
   * Obtiene períodos de un empleado
   */
  async getEmployeePeriods(empleadoId: number, proyectoId: number, anio?: number, mes?: number): Promise<TimePeriod[]> {
    const params = new URLSearchParams();
    params.append('empleado_id', empleadoId.toString());
    params.append('proyecto_id', proyectoId.toString());
    if (anio) params.append('anio', anio.toString());
    if (mes) params.append('mes', mes.toString());

    const queryString = params.toString();
    const url = `${API_ENDPOINTS.APPROVALS}/periods?${queryString}`;
    
    const result = await apiFetch<{ periods: TimePeriod[] }>(url);
    return result.periods || [];
  },

  /**
   * Obtiene períodos pendientes de aprobación para un proyecto
   */
  async getPendingPeriods(proyectoId: number): Promise<TimePeriod[]> {
    const result = await apiFetch<{ periods: TimePeriod[] }>(
      `${API_ENDPOINTS.APPROVALS}/pending?proyecto_id=${proyectoId}`
    );
    return result.periods || [];
  },

  /**
   * Aprueba un período de tiempo
   */
  async approvePeriod(periodId: number, data: ApprovePeriodRequest = {}): Promise<PeriodActionResponse> {
    return apiFetch<PeriodActionResponse>(
      `${API_ENDPOINTS.APPROVALS}/periods/${periodId}/approve`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Rechaza un período de tiempo
   */
  async rejectPeriod(periodId: number, data: RejectPeriodRequest): Promise<PeriodActionResponse> {
    return apiFetch<PeriodActionResponse>(
      `${API_ENDPOINTS.APPROVALS}/periods/${periodId}/reject`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Reabre un período de tiempo cerrado
   */
  async reopenPeriod(periodId: number, data: ReopenPeriodRequest): Promise<PeriodActionResponse> {
    return apiFetch<PeriodActionResponse>(
      `${API_ENDPOINTS.APPROVALS}/periods/${periodId}/reopen`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Obtiene el historial de cambios de estado de un período
   */
  async getPeriodHistory(empleadoId: number, anio: number, mes: number): Promise<ApprovalHistory[]> {
    const params = new URLSearchParams();
    params.append('empleado_id', empleadoId.toString());
    params.append('anio', anio.toString());
    params.append('mes', mes.toString());

    const queryString = params.toString();
    const url = `${API_ENDPOINTS.APPROVALS}/history?${queryString}`;
    
    const result = await apiFetch<{ history: ApprovalHistory[] }>(url);
    return result.history || [];
  }
};
