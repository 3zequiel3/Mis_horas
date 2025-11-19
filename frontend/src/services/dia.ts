import type { Dia } from '../types';
import { ApiService } from './api';

/**
 * Servicio para gestionar días
 * Extiende ApiService para reutilizar lógica de autenticación
 */
export class DiaService extends ApiService {
  /**
   * Obtiene todos los días de un mes específico, opcionalmente filtrados por empleado
   */
  static async getDiasMes(
    proyecto_id: number,
    anio: number,
    mes: number,
    empleado_id?: number
  ): Promise<Dia[]> {
    const url = empleado_id 
      ? `/api/dias/mes/${proyecto_id}/${anio}/${mes}?empleado_id=${empleado_id}`
      : `/api/dias/mes/${proyecto_id}/${anio}/${mes}`;
    return this.get(url);
  }

  /**
   * Obtiene un día específico por ID
   */
  static async getDia(dia_id: number): Promise<Dia> {
    return this.get(`/api/dias/${dia_id}`);
  }

  /**
   * Actualiza las horas de un día
   */
  static async updateHoras(dia_id: number, horas: string): Promise<Dia> {
    return this.put(`/api/dias/${dia_id}/horas`, { horas });
  }

  /**
   * Actualiza horarios de entrada y salida de un día (calcula horas_trabajadas automáticamente)
   */
  static async updateHorarios(dia_id: number, hora_entrada: string, hora_salida: string): Promise<Dia> {
    return this.put(`/api/dias/${dia_id}/horarios`, { hora_entrada, hora_salida });
  }
}
