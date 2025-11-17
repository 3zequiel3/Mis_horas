import type { Dia } from '../types';
import { ApiService } from './api';

/**
 * Servicio para gestionar días
 * Extiende ApiService para reutilizar lógica de autenticación
 */
export class DiaService extends ApiService {
  /**
   * Obtiene todos los días de un mes específico
   */
  static async getDiasMes(
    proyecto_id: number,
    anio: number,
    mes: number
  ): Promise<Dia[]> {
    return this.get(`/api/dias/mes/${proyecto_id}/${anio}/${mes}`);
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
}
