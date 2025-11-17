import type { Proyecto, CreateProyectoRequest, Estadisticas } from '../types';
import { ApiService } from './api';

/**
 * Servicio para gestionar proyectos
 * Extiende ApiService para reutilizar lógica de autenticación y peticiones HTTP
 */
export class ProyectosService extends ApiService {
  /**
   * Obtiene todos los proyectos del usuario autenticado
   */
  static async getProyectos(): Promise<Proyecto[]> {
    return this.get('/api/proyectos');
  }

  /**
   * Crea un nuevo proyecto
   */
  static async createProyecto(data: CreateProyectoRequest): Promise<Proyecto> {
    return this.post('/api/proyectos', data);
  }

  /**
   * Obtiene un proyecto específico por ID
   */
  static async getProyecto(proyectoId: number): Promise<Proyecto> {
    return this.get(`/api/proyectos/${proyectoId}`);
  }

  /**
   * Obtiene los meses disponibles de un proyecto
   */
  static async getMeses(proyectoId: number): Promise<[number, number][]> {
    return this.get(`/api/proyectos/${proyectoId}/meses`);
  }

  /**
   * Agrega un nuevo mes a un proyecto
   */
  static async addMes(proyectoId: number, anio: number, mes: number): Promise<void> {
    return this.post(`/api/proyectos/${proyectoId}/meses`, { anio, mes });
  }

  /**
   * Cambia el estado (activo/inactivo) de un proyecto
   */
  static async cambiarEstado(proyectoId: number, activo: boolean): Promise<void> {
    return this.put(`/api/proyectos/${proyectoId}/estado`, { activo });
  }

  /**
   * Obtiene estadísticas del usuario (proyectos activos, horas, etc)
   */
  static async getEstadisticas(): Promise<Estadisticas> {
    return this.get('/api/proyectos/estadisticas');
  }

  /**
   * Elimina un proyecto
   */
  static async deleteProyecto(proyectoId: number): Promise<void> {
    return this.delete(`/api/proyectos/${proyectoId}`);
  }
}
