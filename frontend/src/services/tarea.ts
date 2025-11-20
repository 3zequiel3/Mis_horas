import type { Tarea } from '../types';
import { ApiService } from './api';

/**
 * Servicio para gestionar tareas
 * Extiende ApiService para reutilizar lógica de autenticación
 */
export class TareaService extends ApiService {
  /**
   * Obtiene todas las tareas de un proyecto
   */
  static async getTareasProyecto(proyecto_id: number): Promise<Tarea[]> {
    return this.get(`/api/tareas/proyecto/${proyecto_id}`);
  }

  /**
   * Crea una nueva tarea
   */
  static async createTarea(
    proyecto_id: number,
    titulo: string,
    detalle?: string,
    que_falta?: string,
    dias_ids?: number[]
  ): Promise<Tarea> {
    return this.post('/api/tareas', {
      proyecto_id,
      titulo,
      detalle,
      que_falta,
      dias_ids,
    });
  }

  /**
   * Obtiene una tarea específica por ID
   */
  static async getTarea(tarea_id: number): Promise<Tarea> {
    return this.get(`/api/tareas/${tarea_id}`);
  }

  /**
   * Actualiza una tarea existente
   */
  static async updateTarea(
    tarea_id: number,
    titulo?: string,
    detalle?: string,
    que_falta?: string,
    dias_ids?: number[]
  ): Promise<Tarea> {
    return this.put(`/api/tareas/${tarea_id}`, {
      titulo,
      detalle,
      que_falta,
      dias_ids,
    });
  }

  /**
   * Elimina una tarea
   */
  static async deleteTarea(tarea_id: number): Promise<{ message: string }> {
    return this.delete(`/api/tareas/${tarea_id}`);
  }

  /**
   * Obtiene los días disponibles para asignar a tareas
   */
  static async getDiasDisponibles(
    proyecto_id: number,
    anio: number,
    mes: number,
    excluir_tarea_id?: number
  ): Promise<any[]> {
    const url = excluir_tarea_id
      ? `/api/tareas/proyecto/${proyecto_id}/disponibles/${anio}/${mes}?excluir_tarea_id=${excluir_tarea_id}`
      : `/api/tareas/proyecto/${proyecto_id}/disponibles/${anio}/${mes}`;
    return this.get(url);
  }

  /**
   * Actualiza las horas de una tarea en un día específico
   */
  static async updateTareaDiaHoras(
    tarea_id: number,
    dia_id: number,
    horas: string
  ): Promise<any> {
    return this.patch(
      `/api/tareas/${tarea_id}/dia/${dia_id}/horas`,
      { horas }
    );
  }
}
