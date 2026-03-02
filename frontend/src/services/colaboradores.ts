/**
 * Servicio de API para Colaboradores
 */

import { apiFetch, API_ENDPOINTS } from '../utils/api';

export interface Colaborador {
  id: number;
  proyecto_id: number;
  usuario_id: number;
  rol: 'owner' | 'colaborador';
  horas_reales_activas: boolean;
  estado: 'pendiente' | 'aceptado' | 'rechazado';
  fecha_invitacion: string;
  fecha_aceptacion?: string;
  fecha_salida?: string;
  usuario?: {
    id: number;
    username: string;
    email: string;
    nombre_completo?: string;
    foto_perfil?: string;
  };
  estadisticas?: {
    total_horas_trabajadas: number;
    total_horas_reales?: number;
  };
}

export interface EstadisticasProyecto {
  total_colaboradores: number;
  total_horas_trabajadas: number;
  total_horas_reales: number;
  top_colaborador?: {
    usuario_id: number;
    nombre: string;
    total_horas: number;
  };
}

export const ColaboradoresService = {
  /**
   * Convierte un proyecto personal a colaborativo
   */
  async convertirAColaborativo(proyectoId: number): Promise<any> {
    const url = `${API_ENDPOINTS.PROYECTOS}/${proyectoId}/convertir-colaborativo`;
    return apiFetch(url, {
      method: 'POST',
    });
  },

  /**
   * Lista todos los colaboradores de un proyecto
   */
  async listar(proyectoId: number, incluirEstadisticas: boolean = false): Promise<Colaborador[]> {
    const params = incluirEstadisticas ? '?incluir_estadisticas=true' : '';
    const url = `${API_ENDPOINTS.PROYECTOS}/${proyectoId}/colaboradores${params}`;
    const response = await apiFetch<{ colaboradores: Colaborador[] }>(url);
    return response.colaboradores;
  },

  /**
   * Invita a un usuario a ser colaborador
   */
  async invitar(
    proyectoId: number,
    email: string,
    horasRealesActivas: boolean = false
  ): Promise<Colaborador> {
    const url = `${API_ENDPOINTS.PROYECTOS}/${proyectoId}/colaboradores`;
    const response = await apiFetch<{ colaborador: Colaborador }>(url, {
      method: 'POST',
      body: JSON.stringify({
        email,
        horas_reales_activas: horasRealesActivas,
      }),
    });
    return response.colaborador;
  },

  /**
   * Elimina un colaborador del proyecto
   */
  async eliminar(proyectoId: number, usuarioId: number): Promise<void> {
    const url = `${API_ENDPOINTS.PROYECTOS}/${proyectoId}/colaboradores/${usuarioId}`;
    await apiFetch(url, {
      method: 'DELETE',
    });
  },

  /**
   * Actualiza la configuración de un colaborador
   */
  async actualizarConfiguracion(
    proyectoId: number,
    usuarioId: number,
    horasRealesActivas: boolean
  ): Promise<Colaborador> {
    const url = `${API_ENDPOINTS.PROYECTOS}/${proyectoId}/colaboradores/${usuarioId}/config`;
    const response = await apiFetch<{ colaborador: Colaborador }>(url, {
      method: 'PUT',
      body: JSON.stringify({
        horas_reales_activas: horasRealesActivas,
      }),
    });
    return response.colaborador;
  },

  /**
   * Obtiene estadísticas del proyecto colaborativo
   */
  async obtenerEstadisticas(proyectoId: number): Promise<EstadisticasProyecto> {
    const url = `${API_ENDPOINTS.PROYECTOS}/${proyectoId}/colaboradores/estadisticas`;
    const response = await apiFetch<{ estadisticas: EstadisticasProyecto }>(url);
    return response.estadisticas;
  },
};
