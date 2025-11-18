import type { Proyecto, Estadisticas } from '../types';
import { ApiService } from './api';

/**
 * Servicio para gestionar un proyecto individual
 * Consolidado con ProyectosService en una interfaz unificada
 */
export class ProyectoService extends ApiService {
  /**
   * Obtiene todos los proyectos del usuario
   */
  static async getProyectos(): Promise<Proyecto[]> {
    return this.get('/api/proyectos');
  }

  /**
   * Crea un nuevo proyecto
   */
  static async createProyecto(
    nombre: string,
    anio: number,
    mes: number,
    descripcion?: string
  ): Promise<Proyecto> {
    return this.post('/api/proyectos', { nombre, anio, mes, descripcion });
  }

  /**
   * Obtiene un proyecto específico por ID
   */
  static async getProyecto(proyecto_id: number): Promise<Proyecto> {
    return this.get(`/api/proyectos/${proyecto_id}`);
  }

  /**
   * Obtiene los meses disponibles de un proyecto
   */
  static async getMeses(proyecto_id: number): Promise<[number, number][]> {
    return this.get(`/api/proyectos/${proyecto_id}/meses`);
  }

  /**
   * Agrega un nuevo mes a un proyecto
   */
  static async addMes(
    proyecto_id: number,
    anio: number,
    mes: number
  ): Promise<{ message: string }> {
    return this.post(`/api/proyectos/${proyecto_id}/meses`, { anio, mes });
  }

  /**
   * Cambia el estado (activo/inactivo) de un proyecto
   */
  static async cambiarEstado(
    proyecto_id: number,
    activo: boolean
  ): Promise<{ message: string }> {
    return this.put(`/api/proyectos/${proyecto_id}/estado`, { activo });
  }

  /**
   * Obtiene estadísticas del usuario
   */
  static async getEstadisticas(): Promise<Estadisticas> {
    return this.get('/api/proyectos/estadisticas');
  }

  /**
   * Actualiza configuración del proyecto
   */
  static async updateConfiguracion(
    proyecto_id: number,
    data: { horas_reales_activas?: boolean }
  ): Promise<Proyecto> {
    return this.put(`/api/proyectos/${proyecto_id}/configuracion`, data);
  }
}
