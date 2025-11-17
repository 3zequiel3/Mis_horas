import type { Tarea, CreateTareaRequest, UpdateTareaRequest } from '../types';
import { getAuthHeaders } from '../utils/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export class TareasService {
  /**
   * Obtiene todas las tareas de un proyecto
   */
  static async getTareasPorProyecto(proyectoId: number): Promise<Tarea[]> {
    const response = await fetch(`${API_URL}/api/tareas?proyecto_id=${proyectoId}`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Error al obtener tareas');
    }

    return response.json();
  }

  /**
   * Obtiene una tarea específica
   */
  static async getTarea(tareaId: number): Promise<Tarea> {
    
    
    const response = await fetch(`${API_URL}/api/tareas/${tareaId}`, {
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) {
      throw new Error('Tarea no encontrada');
    }

    return response.json();
  }

  /**
   * Crea una nueva tarea
   */
  static async createTarea(data: CreateTareaRequest): Promise<Tarea> {
    
    
    const response = await fetch(`${API_URL}/api/tareas`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al crear tarea');
    }

    return response.json();
  }

  /**
   * Actualiza una tarea existente
   */
  static async updateTarea(tareaId: number, data: UpdateTareaRequest): Promise<Tarea> {
    
    
    const response = await fetch(`${API_URL}/api/tareas/${tareaId}`, {
      method: 'PUT',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al actualizar tarea');
    }

    return response.json();
  }

  /**
   * Elimina una tarea
   */
  static async deleteTarea(tareaId: number): Promise<void> {
    
    
    const response = await fetch(`${API_URL}/api/tareas/${tareaId}`, {
      method: 'DELETE',
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al eliminar tarea');
    }
  }
}
