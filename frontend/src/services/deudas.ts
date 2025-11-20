import { ApiService } from './api';
import type { DeudaHoras, Justificacion, JustificarDeudaRequest } from '../types';

/**
 * Servicio para gestionar deudas de horas y justificaciones
 */
export class DeudasService extends ApiService {
  /**
   * Obtiene las deudas de horas del empleado actual
   * Backend retorna array de deudas, no objeto único
   */
  static async obtenerDeudaEmpleado(params: {
    proyecto_id: number;
    empleado_id: number;
    estado?: 'activa' | 'justificada' | 'compensada' | 'cerrada';
  }): Promise<DeudaHoras[]> {
    const queryParams = new URLSearchParams({
      proyecto_id: params.proyecto_id.toString(),
      empleado_id: params.empleado_id.toString(),
    });
    
    if (params.estado) {
      queryParams.append('estado', params.estado);
    }

    return this.get(`/api/deudas/empleado?${queryParams.toString()}`);
  }

  /**
   * Obtiene una deuda específica por ID
   */
  static async obtenerDeuda(deudaId: number): Promise<DeudaHoras> {
    return this.get(`/api/deudas/${deudaId}`);
  }

  /**
   * Justifica una deuda de horas
   */
  static async justificarDeuda(
    deudaId: number,
    data: JustificarDeudaRequest
  ): Promise<Justificacion> {
    return this.post(`/api/deudas/${deudaId}/justificar`, data);
  }

  /**
   * Aprueba una justificación (solo admin)
   */
  static async aprobarJustificacion(
    justificacionId: number,
    data?: { observaciones_admin?: string }
  ): Promise<Justificacion> {
    return this.put(`/api/deudas/justificaciones/${justificacionId}/aprobar`, data);
  }

  /**
   * Rechaza una justificación (solo admin)
   */
  static async rechazarJustificacion(
    justificacionId: number,
    data: { observaciones_admin: string }
  ): Promise<Justificacion> {
    return this.put(`/api/deudas/justificaciones/${justificacionId}/rechazar`, data);
  }

  /**
   * Obtiene todas las justificaciones de un proyecto (solo admin)
   */
  static async obtenerJustificacionesProyecto(
    proyectoId: number,
    params?: {
      estado?: 'pendiente' | 'aprobada' | 'rechazada';
      empleado_id?: number;
    }
  ): Promise<Justificacion[]> {
    let url = `/api/deudas/justificaciones/proyecto/${proyectoId}`;
    
    if (params) {
      const queryParams = new URLSearchParams();
      if (params.estado) queryParams.append('estado', params.estado);
      if (params.empleado_id) queryParams.append('empleado_id', params.empleado_id.toString());
      
      if (queryParams.toString()) {
        url += `?${queryParams.toString()}`;
      }
    }

    return this.get(url);
  }

  /**
   * Obtiene las justificaciones del empleado actual
   */
  static async obtenerJustificacionesEmpleado(params: {
    proyecto_id: number;
    empleado_id: number;
    estado?: 'pendiente' | 'aprobada' | 'rechazada';
  }): Promise<Justificacion[]> {
    const queryParams = new URLSearchParams({
      proyecto_id: params.proyecto_id.toString(),
      empleado_id: params.empleado_id.toString(),
    });

    if (params.estado) {
      queryParams.append('estado', params.estado);
    }

    return this.get(`/api/deudas/justificaciones/empleado?${queryParams.toString()}`);
  }
}
